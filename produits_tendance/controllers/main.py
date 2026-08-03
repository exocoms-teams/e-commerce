import json
import os
from odoo import http
from odoo.http import request
from ..collecte_scrapers.ebay_ingestor import run_ingestion_for_keyword

from .dashboard_api import TrendDashboardAPI

# -----------------------------------------------------------
# 1. CONTROLEUR DU FORMULAIRE WEB (Frontend)
# -----------------------------------------------------------
class TrendSubmissionController(http.Controller):

    # Route pour AFFICHER le formulaire (GET)
    @http.route('/submit-trend', type='http', auth='public', website=True)
    def submit_trend_form(self, **kwargs):
        return request.render('produits_tendance.template_submit_trend_form', {})

    # Route pour TRAITER le formulaire (POST)
    @http.route('/submit-trend/process', type='http', auth='public', website=True, methods=['POST'], csrf=True)
    def submit_trend_process(self, **post):
        if post:
            # --- NOUVELLE LOGIQUE : Tri intelligent Lien ou Description ---
            # On récupère le champ unique du formulaire web
            user_input = post.get('link_or_desc', '').strip()
            final_ref = False
            final_desc = False
            
            # Si ça commence par http et qu'il n'y a pas d'espaces, c'est un lien
            if user_input.startswith('http') and ' ' not in user_input:
                final_ref = user_input
            # Sinon, on considère que c'est une description texte
            else:
                final_desc = user_input
            # --------------------------------------------------------------

            # sudo() permet au visiteur non connecté de créer l'enregistrement sans bloquer sur les droits
            request.env['trend.submission'].sudo().create({
                'name': post.get('name'),
                'product_ref': final_ref,  # Sera rempli si c'est un lien (sinon False)
                'description': final_desc, # Sera rempli si c'est du texte (sinon False)
                'category': post.get('category'),
                'country': post.get('country'),
                'submission_reason': post.get('submission_reason'),
                'email': post.get('email'),
                'submitted_by': request.env.user.name if request.env.user.name != 'Public user' else 'Visiteur Anonyme',
            })
        # Redirection vers la page avec un message de succès
        return request.redirect('/submit-trend?success=1')


# -----------------------------------------------------------
# 2. CONTROLEUR FICHE PRODUIT DETAILLEE (Frontend)
# -----------------------------------------------------------
class TrendProductDetailController(http.Controller):

    @http.route('/product/<int:id>', type='http', auth='public', website=True)
    def product_detail(self, id, **kwargs):
        # NB : get_product_detail lève werkzeug.exceptions.NotFound si
        # l'id n'existe pas. On laisse volontairement l'exception remonter :
        # sur une route website=True, Odoo l'intercepte lui-même et affiche
        # la page 404 du thème (pas de try/except ici, pas de stacktrace).
        api = TrendDashboardAPI(request.env)
        data = api.get_product_detail(id)
        return request.render('produits_tendance.template_product_detail', data)


# -----------------------------------------------------------
# 2bis. CONTROLEUR DASHBOARD (Classement des produits & Ingestion)
# -----------------------------------------------------------
class TrendDashboardController(http.Controller):

    @http.route('/dashboard', type='http', auth='user', website=True)
    def dashboard(self, **kwargs):
        limit = 5 if request.env.user.has_group('produits_tendance.group_trend_free') else None
        api = TrendDashboardAPI(request.env)
        products = api.get_dashboard_products(limit=limit)

        return request.render('produits_tendance.winners_dashboard_template', {
            'products': products,
        })

    # Route pour AFFICHER le Dashboard d'ingestion eBay
    @http.route('/winners/dashboard', type='http', auth='user', website=True)
    def show_dashboard(self, **kwargs):
        return request.render('produits_tendance.template_winners_dashboard', {})

    # Route JSON pour EXECUTER le script eBay (Appel AJAX)
    @http.route('/dashboard/run_ebay_scan', type='jsonrpc', auth='user')
    def run_ebay_scan(self, keyword):
        if not keyword:
            return {"status": "error", "message": "Mot-clé manquant."}

        result = run_ingestion_for_keyword(keyword)
        
        return result


# -----------------------------------------------------------
# 3. CONTROLEUR DE L'API (Réception des données de l'extension)
# -----------------------------------------------------------
class TrendIngestController(http.Controller):

    @http.route('/api/trend/ingest', type='http', auth='none', methods=['POST'], csrf=False)
    def ingest(self, **kwargs):
        try:
            data = json.loads(request.httprequest.data)
        except Exception:
            return self._json_response({'status': 'error', 'code': 'invalid_json'}, 400)

        api_key = data.get('api_key')
        if not api_key:
            return self._json_response(
                {'status': 'error', 'code': 'missing_field', 'field': 'api_key'}, 401
            )
        if not self.check_api_key(api_key):
            return self._json_response(
                {'status': 'error', 'code': 'invalid_api_key'}, 403
            )

        data_type = data.get('type')
        if not data_type:
            return self._json_response(
                {'status': 'error', 'code': 'missing_field', 'field': 'type'}, 400
            )

        payload = data.get('data', {})
        return self.route_by_type(data_type, payload)

    def route_by_type(self, type, data):
        if type == 'product':
            return self._handle_product(data)
        elif type == 'ad':
            return self._handle_ad(data)
        elif type == 'score':
            return self._handle_score(data)
        else:
            return self._json_response(
                {'status': 'error', 'code': 'unknown_type', 'field': 'type', 'received': type}, 400
            )

    def _handle_product(self, payload):
        required_fields = ['name', 'product_ref', 'category', 'country', 'source']
        for field in required_fields:
            if not payload.get(field):
                return self._json_response(
                    {'status': 'error', 'code': 'missing_field', 'field': field}, 400
                )

        env = request.env(su=True)

        category = env['trend.category'].search(
            [('name', '=', payload['category'])], limit=1
        )
        if not category:
            category = env['trend.category'].create({'name': payload['category']})

        existing = env['trend.product'].search([
            ('product_ref', '=', payload['product_ref']),
            ('source', '=', payload['source']),
        ], limit=1)

        vals = {
            'name': payload['name'],
            'product_ref': payload['product_ref'],
            'category_id': category.id,
            'sales_count': payload.get('sales_count', 0),
            'date': payload.get('date'),
            'score_site_x': payload.get('score_site_x'),
            'country': payload['country'],
            'source': payload['source'],
            'image_url': payload.get('image_url'),
        }
        vals = {k: v for k, v in vals.items() if v is not None}

        if existing:
            existing.write(vals)
            record = existing
        else:
            record = env['trend.product'].create(vals)

        return self._json_response(
            {'status': 'success', 'type': 'product', 'id': record.id}, 200
        )

    def _handle_ad(self, payload):
        required_fields = ['ad_ref', 'product_ref', 'country', 'social_network']
        for field in required_fields:
            if not payload.get(field):
                return self._json_response(
                    {'status': 'error', 'code': 'missing_field', 'field': field}, 400
                )

        env = request.env(su=True)

        existing = env['trend.ad'].search(
            [('ad_ref', '=', payload['ad_ref'])], limit=1
        )

        vals = {
            'ad_ref': payload['ad_ref'],
            'product_ref': payload['product_ref'],
            'country': payload['country'],
            'social_network': payload['social_network'],
            'likes_count': payload.get('likes_count', 0),
            'shares_count': payload.get('shares_count', 0),
        }

        if existing:
            existing.write(vals)
            record = existing
        else:
            record = env['trend.ad'].create(vals)

        return self._json_response(
            {'status': 'success', 'type': 'ad', 'id': record.id}, 200
        )

    def _handle_score(self, payload):
        required_fields = ['product_ref', 'computed_score']
        for field in required_fields:
            if not payload.get(field):
                return self._json_response(
                    {'status': 'error', 'code': 'missing_field', 'field': field}, 400
                )

        env = request.env(su=True)

        product = env['trend.product'].search(
            [('product_ref', '=', payload['product_ref'])], limit=1
        )
        if not product:
            return self._json_response(
                {'status': 'error', 'code': 'product_not_found',
                 'product_ref': payload['product_ref']}, 404
            )

        vals = {
            'product_id': product.id,
            'computed_score': payload['computed_score'],
        }
        if payload.get('computed_at'):
            vals['computed_at'] = payload['computed_at']

        record = env['trend.score'].create(vals)

        return self._json_response(
            {'status': 'success', 'type': 'score', 'id': record.id}, 200
        )

    def check_api_key(self, key):
        import os
        valid_key = os.getenv('ODOO_API_KEY')
        return valid_key and key == valid_key

    def _json_response(self, payload, status):
        return request.make_response(
            json.dumps(payload),
            status=status,
            headers=[('Content-Type', 'application/json')]
        )
