# -*- coding: utf-8 -*-
"""
API REST — Assurances & PWA Intervenants
Auth assurance : Header X-API-KEY
Auth PWA       : Session Odoo (auth='user')
"""
import json
import logging
from functools import wraps
from odoo import http, _
from odoo.http import request, Response

_logger = logging.getLogger(__name__)


def require_api_key(func):
    @wraps(func)
    def wrapper(self, *args, **kwargs):
        api_key = request.httprequest.headers.get('X-API-KEY')
        if not api_key:
            return _err(401, "Header X-API-KEY manquant")
        assurance = request.env['sinistre.assurance'].sudo().search(
            [('api_key', '=', api_key), ('api_key_active', '=', True), ('actif', '=', True)], limit=1)
        if not assurance:
            return _err(403, "Clé API invalide ou désactivée")
        return func(self, assurance=assurance, *args, **kwargs)
    return wrapper


def _ok(data, status=200):
    return Response(json.dumps(data, default=str, ensure_ascii=False), status=status,
                    content_type='application/json; charset=utf-8')

def _err(status, msg, detail=None):
    body = {'success': False, 'error': msg}
    if detail:
        body['detail'] = detail
    return _ok(body, status)


class SinistreApiController(http.Controller):

    @http.route('/api/sinistre/v1/ping', type='http', auth='public', methods=['GET'], csrf=False)
    def ping(self, **kw):
        return _ok({'success': True, 'message': 'API Sinistre Services opérationnelle'})

    # ── ASSURANCE : créer mission ────────────────────────────────────
    @http.route('/api/sinistre/v1/mission', type='http', auth='public', methods=['POST'], csrf=False)
    @require_api_key
    def creer_mission(self, assurance=None, **kw):
        try:
            body = json.loads(request.httprequest.data.decode('utf-8'))
        except Exception as e:
            return _err(400, "JSON invalide", str(e))

        for f in ['type_intervention', 'description', 'adresse_intervention', 'client']:
            if not body.get(f):
                return _err(400, f"Champ obligatoire manquant : {f}")

        client_data = body['client']
        if not client_data.get('nom'):
            return _err(400, "client.nom obligatoire")

        env = request.env(su=True)
        partner = _get_or_create_partner(env, client_data)

        types_ok = ['serrurerie', 'plomberie', 'menuiserie_int', 'menuiserie_ext', 'vitrerie', 'electricite', 'autre']
        type_int = body.get('type_intervention', 'autre')
        if type_int not in types_ok:
            return _err(400, f"type_intervention invalide. Valeurs : {types_ok}")

        urgence = body.get('urgence', 'normale')
        if urgence not in ('normale', 'urgente', 'tres_urgente'):
            urgence = 'normale'

        try:
            m = env['sinistre.mission'].create({
                'source': 'assurance',
                'assurance_id': assurance.id,
                'ref_assurance': body.get('ref_assurance', ''),
                'contrat_assurance': body.get('contrat', ''),
                'client_id': partner.id,
                'type_intervention': type_int,
                'urgence': urgence,
                'priority': '2' if urgence == 'tres_urgente' else ('1' if urgence == 'urgente' else '0'),
                'description_sinistre': body.get('description', ''),
                'adresse_intervention': body.get('adresse_intervention', ''),
                'contact_sur_place': body.get('contact_sur_place', ''),
                'tel_sur_place': body.get('tel_sur_place', ''),
                'montant_garanti': float(body.get('montant_garanti', 0)),
                'franchise': float(body.get('franchise', 0)),
            })
            return _ok({'success': True, 'reference': m.reference, 'token': m.token_api,
                        'state': m.state, 'suivi_url': f"/suivi/{m.token_api}"}, 201)
        except Exception as e:
            _logger.error(f"API creer_mission: {e}")
            return _err(500, "Erreur interne", str(e))

    # ── ASSURANCE : statut mission ───────────────────────────────────
    @http.route('/api/sinistre/v1/mission/<string:reference>', type='http', auth='public', methods=['GET'], csrf=False)
    @require_api_key
    def get_mission(self, reference, assurance=None, **kw):
        m = request.env['sinistre.mission'].sudo().search(
            [('reference', '=', reference), ('assurance_id', '=', assurance.id)], limit=1)
        if not m:
            return _err(404, f"Mission {reference} introuvable")
        return _ok({'success': True, 'mission': {
            'reference': m.reference, 'ref_assurance': m.ref_assurance,
            'state': m.state, 'type_intervention': m.type_intervention,
            'intervenant': m.intervenant_id.name if m.intervenant_id else None,
            'date_rdv': str(m.date_rdv) if m.date_rdv else None,
            'date_debut': str(m.date_debut_travaux) if m.date_debut_travaux else None,
            'date_cloture': str(m.date_cloture) if m.date_cloture else None,
            'montant_devis': m.montant_devis, 'montant_garanti': m.montant_garanti,
            'reste_a_charge': m.reste_a_charge,
            'photos_avant': m.photos_avant_count, 'photos_apres': m.photos_apres_count,
        }})

    # ── ASSURANCE : liste missions ───────────────────────────────────
    @http.route('/api/sinistre/v1/missions', type='http', auth='public', methods=['GET'], csrf=False)
    @require_api_key
    def list_missions(self, assurance=None, **kw):
        params = request.params
        domain = [('assurance_id', '=', assurance.id)]
        if params.get('state'):
            domain.append(('state', '=', params['state']))
        if params.get('date_from'):
            domain.append(('date_reception', '>=', params['date_from']))
        missions = request.env['sinistre.mission'].sudo().search(domain, limit=200, order='date_reception desc')
        return _ok({'success': True, 'count': len(missions), 'missions': [{
            'reference': m.reference, 'ref_assurance': m.ref_assurance,
            'state': m.state, 'type_intervention': m.type_intervention,
            'date_reception': str(m.date_reception), 'client': m.client_id.name,
            'adresse': m.adresse_intervention,
        } for m in missions]})

    # ── PUBLIC : demande directe ─────────────────────────────────────
    @http.route('/api/sinistre/v1/demande', type='http', auth='public', methods=['POST'], csrf=False)
    def creer_demande(self, **kw):
        try:
            body = json.loads(request.httprequest.data.decode('utf-8'))
        except Exception as e:
            return _err(400, "JSON invalide", str(e))

        for f in ['type_intervention', 'description', 'adresse_intervention', 'client']:
            if not body.get(f):
                return _err(400, f"Champ obligatoire : {f}")

        env = request.env(su=True)
        partner = _get_or_create_partner(env, body['client'])
        source = body.get('source', 'particulier')
        if source not in ('particulier', 'entreprise'):
            source = 'particulier'

        try:
            m = env['sinistre.mission'].create({
                'source': source,
                'client_id': partner.id,
                'type_intervention': body.get('type_intervention', 'autre'),
                'urgence': body.get('urgence', 'normale'),
                'description_sinistre': body.get('description', ''),
                'adresse_intervention': body.get('adresse_intervention', ''),
                'tel_sur_place': body.get('client', {}).get('tel', ''),
                'origine_web': True,
            })
            return _ok({'success': True, 'reference': m.reference, 'token': m.token_api,
                        'suivi_url': f"/suivi/{m.token_api}",
                        'message': 'Demande enregistrée, nous vous contacterons rapidement.'}, 201)
        except Exception as e:
            return _err(500, "Erreur interne", str(e))

    # ── PWA INTERVENANT : mes missions ───────────────────────────────
    @http.route('/api/sinistre/v1/intervenant/missions', type='http', auth='user', methods=['GET'], csrf=False)
    def mes_missions(self, **kw):
        intervenant = request.env['sinistre.intervenant'].sudo().search([('user_id', '=', request.env.user.id)], limit=1)
        if not intervenant:
            return _err(403, "Aucun intervenant associé à ce compte")
        missions = request.env['sinistre.mission'].search([
            ('intervenant_id', '=', intervenant.id),
            ('state', 'not in', ('clos', 'annule')),
        ], order='urgence desc, date_rdv asc')
        return _ok({'success': True, 'missions': [{
            'id': m.id, 'reference': m.reference, 'state': m.state,
            'type_intervention': m.type_intervention, 'urgence': m.urgence,
            'adresse': m.adresse_intervention, 'client': m.client_id.name,
            'tel_sur_place': m.tel_sur_place or '',
            'date_rdv': str(m.date_rdv) if m.date_rdv else None,
            'description': m.description_sinistre,
            'photos_avant': m.photos_avant_count, 'photos_apres': m.photos_apres_count,
            'montant_devis': m.montant_devis, 'reste_a_charge': m.reste_a_charge,
        } for m in missions]})


def _get_or_create_partner(env, data):
    email = data.get('email', '')
    partner = env['res.partner'].search([('email', '=', email)], limit=1) if email else None
    if not partner:
        nom = data.get('nom', '')
        prenom = data.get('prenom', '')
        is_company = data.get('is_company', False)
        partner = env['res.partner'].create({
            'name': f"{prenom} {nom}".strip() if not is_company else nom or 'Client Inconnu',
            'email': email,
            'phone': data.get('tel', ''),
            'is_company': is_company,
        })
    return partner
