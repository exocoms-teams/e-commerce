import hmac
import json
import os
import re
from odoo import http
from odoo.http import request
from ..collecte_scrapers.ebay_ingestor import run_ingestion_for_keyword
from ..collecte_scrapers.meta_ingestor import run_meta_ingestion
from .dashboard_api import TrendDashboardAPI

# -----------------------------------------------------------
# 1. CONTROLEUR DU FORMULAIRE WEB (Frontend)
# -----------------------------------------------------------
class TrendSubmissionController(http.Controller):

    @http.route('/submit-trend', type='http', auth='public', website=True)
    def submit_trend_form(self, **kwargs):
        return request.render('produits_tendance.template_submit_trend_form', {})

    @http.route('/submit-trend/process', type='http', auth='public', website=True, methods=['POST'], csrf=True)
    def submit_trend_process(self, **post):
        if post:
            # --- NOUVELLE LOGIQUE : Tri intelligent Lien ou Description ---
            user_input = post.get('link_or_desc', '').strip()
            final_ref = False
            final_desc = False
            
            if user_input.startswith('http') and ' ' not in user_input:
                final_ref = user_input
            else:
                final_desc = user_input

            request.env['trend.submission'].sudo().create({
                'name': post.get('name'),
                'product_ref': final_ref,
                'description': final_desc,
                'category': post.get('category'),
                'country': post.get('country'),
                'submission_reason': post.get('submission_reason'),
                'email': post.get('email'),
                'submitted_by': request.env.user.name if request.env.user.name != 'Public user' else 'Visiteur Anonyme',
            })
        return request.redirect('/submit-trend?success=1')

# -----------------------------------------------------------
# 2. CONTROLEUR FICHE PRODUIT DETAILLEE (Frontend)
# -----------------------------------------------------------
class TrendProductDetailController(http.Controller):

    @http.route('/product/<int:id>', type='http', auth='public', website=True)
    def product_detail(self, id, **kwargs):
        api = TrendDashboardAPI(request.env)
        data = api.get_product_detail(id)
        return request.render('produits_tendance.template_product_detail', data)

# -----------------------------------------------------------
# 2bis. CONTROLEUR DASHBOARD (Classement des produits & Ingestion)
# -----------------------------------------------------------
class TrendDashboardController(http.Controller):

    @http.route('/dashboard', type='http', auth='public', website=True)
    def dashboard(self, **kwargs):
        """Affiche la page dashboard (classement produits) avec le panneau
        de filtres et la limite Freemium (WIN-48).
        """
        limit = 5 if request.env.user.has_group('produits_tendance.group_trend_free') else None
        
        api = TrendDashboardAPI(request.env)
        options = api.get_filter_options()
        stats = api.get_dashboard_stats()

        return request.render('produits_tendance.template_dashboard', {
            'products': api.get_product_list(limit=limit),
            'categories': options.get('categories', []),
            'countries': options.get('countries', []),
            'total_products': stats['total_products'],
            'avg_score': stats['avg_score'],
        })

    @http.route('/api/dashboard/filter', type='http', auth='public', methods=['GET'], csrf=False)
    def dashboard_filter(self, category_id=None, country=None, **kwargs):
        """Route JSON interne consommée en AJAX par dashboard_filters.js.

        Applique la meme limite Freemium (WIN-48) que le rendu initial :
        sans ca, un compte Freemium filtrant via le panneau contournerait
        la limite de 5 produits (celle-ci n'etait appliquee que sur le
        rendu QWeb initial, jamais sur cette route AJAX)."""
        limit = 5 if request.env.user.has_group('produits_tendance.group_trend_free') else None
        api = TrendDashboardAPI(request.env)
        products = api.get_product_list(
            category_id=category_id or None, country=country or None, limit=limit,
        )
        return request.make_response(
            json.dumps({'status': 'success', 'products': products}),
            headers=[('Content-Type', 'application/json')],
        )

    # Route pour AFFICHER le Dashboard d'ingestion eBay/Meta
    @http.route('/winners/dashboard', type='http', auth='user', website=True)
    def show_dashboard(self, **kwargs):
        return request.render('produits_tendance.template_winners_dashboard', {})
    
    # --- ROUTE EBAY ---
    @http.route('/dashboard/run_ebay_scan', type='jsonrpc', auth='user')
    def run_ebay_scan(self, keyword):
        is_api_user = request.env.user.has_group('produits_tendance.group_trend_api')
        is_admin = request.env.user.has_group('base.group_erp_manager')
        
        if not (is_api_user or is_admin):
            return {"status": "error", "message": "Accès refusé : Vous n'avez pas les droits pour lancer le scan."}

        if not keyword:
            return {"status": "error", "message": "Mot-clé manquant."}

        Param = request.env['ir.config_parameter'].sudo()
        ebay_app_id = Param.get_param('ebay.app_id')
        ebay_cert_id = Param.get_param('ebay.cert_id')
        odoo_api_key = Param.get_param('winners.api_key')
        
        base_url = Param.get_param('web.base.url')
        odoo_url = f"{base_url}/api/trend/ingest"
        
        result = run_ingestion_for_keyword(
            keyword=keyword,
            app_id=ebay_app_id,
            cert_id=ebay_cert_id,
            odoo_url=odoo_url,
            odoo_api_key=odoo_api_key
        )
        
        return result

    # --- ROUTE META ADS (MANUELLE) ---
    @http.route('/dashboard/run_meta_scan', type='jsonrpc', auth='user')
    def run_meta_scan(self, keyword):
        is_api_user = request.env.user.has_group('produits_tendance.group_trend_api')
        is_admin = request.env.user.has_group('base.group_erp_manager')
        
        if not (is_api_user or is_admin):
            return {"status": "error", "message": "Accès refusé : Vous n'avez pas les droits pour lancer le scan."}

        if not keyword:
            return {"status": "error", "message": "Mot-clé manquant."}

        Param = request.env['ir.config_parameter'].sudo()
        meta_token = Param.get_param('meta.access_token')
        odoo_api_key = Param.get_param('winners.api_key')
        base_url = Param.get_param('web.base.url')
        odoo_url = f"{base_url}/api/trend/ingest"

        if not meta_token:
            return {"status": "error", "message": "Clé Meta introuvable. Veuillez configurer 'meta.access_token' dans les paramètres système."}

        result = run_meta_ingestion(
            keyword=keyword,
            access_token=meta_token,
            odoo_url=odoo_url,
            odoo_api_key=odoo_api_key
        )
        
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
            return self._json_response({'status': 'error', 'code': 'missing_field', 'field': 'api_key'}, 401)
            
        if not self.check_api_key(api_key):
            return self._json_response({'status': 'error', 'code': 'invalid_api_key'}, 403)

        data_type = data.get('type')
        if not data_type:
            return self._json_response({'status': 'error', 'code': 'missing_field', 'field': 'type'}, 400)

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
            return self._json_response({'status': 'error', 'code': 'unknown_type', 'field': 'type', 'received': type}, 400)

    def _handle_product(self, payload):
        required_fields = ['name', 'product_ref', 'category', 'country', 'source']
        for field in required_fields:
            if not payload.get(field):
                return self._json_response({'status': 'error', 'code': 'missing_field', 'field': field}, 400)

        env = request.env(su=True)

        category = env['trend.category'].search([('name', '=', payload['category'])], limit=1)
        if not category:
            category = env['trend.category'].create({'name': payload['category']})

        existing = env['trend.product'].search([
            ('product_ref', '=', payload['product_ref']),
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

        return self._json_response({'status': 'success', 'type': 'product', 'id': record.id}, 200)

    def _handle_ad(self, payload):
        required_fields = ['ad_ref', 'product_ref', 'country', 'social_network']
        for field in required_fields:
            if not payload.get(field):
                return self._json_response({'status': 'error', 'code': 'missing_field', 'field': field}, 400)

        env = request.env(su=True)

        # Création / Recherche automatique du produit rattaché
        product = env['trend.product'].search([('product_ref', '=', payload['product_ref'])], limit=1)
        
        if not product:
            category = env['trend.category'].search([('name', '=', 'Non classé')], limit=1)
            if not category:
                category = env['trend.category'].create({'name': 'Non classé'})
                
            product = env['trend.product'].create({
                'name': payload.get('product_name', 'Produit Généré par Meta'),
                'product_ref': payload['product_ref'],
                'category_id': category.id,
                'country': payload['country'],
                'source': 'api',
            })

        vals = {
            'ad_ref': payload['ad_ref'],
            'product_ref': payload['product_ref'],
            'product_id': product.id,
            'country': payload['country'],
            'social_network': payload['social_network'],
            # Champs TrendTracker
            'days_active': payload.get('days_active', 0),
            'ad_start_date': payload.get('ad_start_date'),
            'competitor_page': payload.get('competitor_page'),
            'snapshot_url': payload.get('snapshot_url'),
            'platforms': payload.get('platforms'),
            'is_active': payload.get('is_active', True),
            # Rétro-compatibilité
            'likes_count': payload.get('likes_count', 0),
            'shares_count': payload.get('shares_count', 0),
        }
        
        # Prise en compte de la date de collecte ajoutée par ton collègue
        if payload.get('collected_at'):
            vals['collected_at'] = payload['collected_at']
            
        record = env['trend.ad'].create(vals)

        return self._json_response({'status': 'success', 'type': 'ad', 'id': record.id}, 200)

    def _handle_score(self, payload):
        required_fields = ['product_ref', 'computed_score']
        for field in required_fields:
            if not payload.get(field):
                return self._json_response({'status': 'error', 'code': 'missing_field', 'field': field}, 400)

        env = request.env(su=True)

        product = env['trend.product'].search([('product_ref', '=', payload['product_ref'])], limit=1)
        if not product:
            return self._json_response({'status': 'error', 'code': 'product_not_found', 'product_ref': payload['product_ref']}, 404)

        vals = {
            'product_id': product.id,
            'computed_score': payload['computed_score'],
        }
        if payload.get('computed_at'):
            vals['computed_at'] = payload['computed_at']

        record = env['trend.score'].create(vals)

        return self._json_response({'status': 'success', 'type': 'score', 'id': record.id}, 200)

    def check_api_key(self, key):
        valid_key = request.env['ir.config_parameter'].sudo().get_param('winners.api_key')
        # hmac.compare_digest() : comparaison en temps constant, plutot que
        # == qui peut fuiter la longueur/le prefixe correct de la cle via
        # une attaque temporelle (Epic 1.D, "Securiser l'endpoint (cle API)").
        return bool(valid_key) and hmac.compare_digest(key, valid_key)
    
    def _json_response(self, payload, status):
        return request.make_response(
            json.dumps(payload),
            status=status,
            headers=[('Content-Type', 'application/json')]
        )