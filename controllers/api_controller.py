# -*- coding: utf-8 -*-
"""
API REST pour la réception des ordres de mission des compagnies d'assurance.

Endpoints :
  POST /api/sinistre/v1/mission          → Créer un ordre de mission
  GET  /api/sinistre/v1/mission/<ref>    → Statut d'une mission
  POST /api/sinistre/v1/mission/<ref>/update → Mise à jour assurance
  GET  /api/sinistre/v1/ping             → Test de connectivité

Authentification : Header  X-API-KEY: <clé_api_assurance>
"""
import json
import logging
from functools import wraps

from odoo import http, _
from odoo.http import request, Response

_logger = logging.getLogger(__name__)


def require_api_key(func):
    """Décorateur : vérifie la clé API et retourne l'assurance associée."""
    @wraps(func)
    def wrapper(self, *args, **kwargs):
        api_key = request.httprequest.headers.get('X-API-KEY')
        if not api_key:
            return _json_error(401, "Clé API manquante (header X-API-KEY requis)")

        assurance = request.env['sinistre.assurance'].sudo().search([
            ('api_key', '=', api_key),
            ('api_key_active', '=', True),
            ('actif', '=', True),
        ], limit=1)

        if not assurance:
            return _json_error(403, "Clé API invalide ou désactivée")

        return func(self, assurance=assurance, *args, **kwargs)
    return wrapper


def _json_response(data, status=200):
    return Response(
        json.dumps(data, default=str, ensure_ascii=False),
        status=status,
        content_type='application/json; charset=utf-8',
    )


def _json_error(status, message, details=None):
    body = {'success': False, 'error': message}
    if details:
        body['details'] = details
    return _json_response(body, status=status)


class SinistreApiController(http.Controller):
    """Contrôleur API pour les assurances et clients directs."""

    # ─── PING ────────────────────────────────────────────────────────
    @http.route('/api/sinistre/v1/ping', type='http', auth='public', methods=['GET'], csrf=False)
    def ping(self, **kwargs):
        """Test de connectivité."""
        return _json_response({'success': True, 'message': 'API Sinistre Services opérationnelle'})

    # ─── CRÉER UNE MISSION (Assurance) ───────────────────────────────
    @http.route('/api/sinistre/v1/mission', type='http', auth='public', methods=['POST'], csrf=False)
    @require_api_key
    def creer_mission_assurance(self, assurance=None, **kwargs):
        """
        Crée un ordre de mission depuis une compagnie d'assurance.

        Body JSON attendu :
        {
            "ref_assurance": "SIN-2025-001234",
            "contrat": "CTR-789456",
            "type_intervention": "serrurerie",  // serrurerie|plomberie|menuiserie_int|menuiserie_ext|vitrerie|electricite|autre
            "urgence": "urgente",               // normale|urgente|tres_urgente
            "description": "Porte fracturée suite à tentative de cambriolage",
            "montant_garanti": 850.00,
            "franchise": 150.00,
            "client": {
                "nom": "Dupont",
                "prenom": "Jean",
                "email": "jean.dupont@email.fr",
                "tel": "0612345678"
            },
            "adresse_intervention": "12 rue de la Paix, 75001 Paris",
            "contact_sur_place": "Mme Dupont",
            "tel_sur_place": "0698765432"
        }
        """
        try:
            body = json.loads(request.httprequest.data.decode('utf-8'))
        except (json.JSONDecodeError, UnicodeDecodeError) as e:
            return _json_error(400, "Body JSON invalide", str(e))

        # Validation champs obligatoires
        required = ['type_intervention', 'description', 'adresse_intervention', 'client']
        missing = [f for f in required if not body.get(f)]
        if missing:
            return _json_error(400, f"Champs obligatoires manquants : {', '.join(missing)}")

        client_data = body.get('client', {})
        if not client_data.get('nom'):
            return _json_error(400, "Le nom du client est obligatoire")

        env = request.env(su=True)

        # Trouver ou créer le partenaire client
        partner = _find_or_create_partner(env, client_data)

        # Types d'intervention valides
        types_valides = ['serrurerie', 'plomberie', 'menuiserie_int', 'menuiserie_ext',
                         'vitrerie', 'electricite', 'autre']
        type_intervention = body.get('type_intervention', 'autre')
        if type_intervention not in types_valides:
            return _json_error(400, f"type_intervention invalide. Valeurs : {types_valides}")

        urgences_valides = ['normale', 'urgente', 'tres_urgente']
        urgence = body.get('urgence', 'normale')
        if urgence not in urgences_valides:
            urgence = 'normale'

        # Créer la mission
        try:
            mission = env['sinistre.mission'].create({
                'source': 'assurance',
                'assurance_id': assurance.id,
                'ref_assurance': body.get('ref_assurance', ''),
                'contrat_assurance': body.get('contrat', ''),
                'client_id': partner.id,
                'type_intervention': type_intervention,
                'urgence': urgence,
                'priority': '1' if urgence == 'urgente' else ('2' if urgence == 'tres_urgente' else '0'),
                'description_sinistre': body.get('description', ''),
                'adresse_intervention': body.get('adresse_intervention', ''),
                'contact_sur_place': body.get('contact_sur_place', ''),
                'tel_sur_place': body.get('tel_sur_place', ''),
                'montant_garanti': float(body.get('montant_garanti', 0)),
                'franchise': float(body.get('franchise', 0)),
            })

            _logger.info(f"Mission créée via API assurance {assurance.name}: {mission.reference}")

            return _json_response({
                'success': True,
                'reference': mission.reference,
                'token': mission.token_api,
                'state': mission.state,
                'message': 'Ordre de mission créé avec succès',
            }, status=201)

        except Exception as e:
            _logger.error(f"Erreur création mission API: {e}")
            return _json_error(500, "Erreur interne lors de la création", str(e))

    # ─── STATUT D'UNE MISSION ────────────────────────────────────────
    @http.route('/api/sinistre/v1/mission/<string:reference>', type='http', auth='public', methods=['GET'], csrf=False)
    @require_api_key
    def get_mission_status(self, reference, assurance=None, **kwargs):
        """Retourne le statut détaillé d'une mission."""
        mission = request.env['sinistre.mission'].sudo().search([
            ('reference', '=', reference),
            ('assurance_id', '=', assurance.id),
        ], limit=1)

        if not mission:
            return _json_error(404, f"Mission {reference} introuvable")

        return _json_response({
            'success': True,
            'mission': {
                'reference': mission.reference,
                'ref_assurance': mission.ref_assurance,
                'state': mission.state,
                'type_intervention': mission.type_intervention,
                'intervenant': mission.intervenant_id.name if mission.intervenant_id else None,
                'date_rdv': str(mission.date_rdv) if mission.date_rdv else None,
                'date_debut_travaux': str(mission.date_debut_travaux) if mission.date_debut_travaux else None,
                'date_cloture': str(mission.date_cloture) if mission.date_cloture else None,
                'montant_devis': mission.montant_devis,
                'montant_garanti': mission.montant_garanti,
                'reste_a_charge': mission.reste_a_charge,
                'photos_avant': mission.photos_avant_count,
                'photos_apres': mission.photos_apres_count,
            }
        })

    # ─── LISTE DES MISSIONS (Assurance) ──────────────────────────────
    @http.route('/api/sinistre/v1/missions', type='http', auth='public', methods=['GET'], csrf=False)
    @require_api_key
    def lister_missions(self, assurance=None, **kwargs):
        """Liste toutes les missions d'une assurance."""
        params = request.params
        domain = [('assurance_id', '=', assurance.id)]

        if params.get('state'):
            domain.append(('state', '=', params['state']))
        if params.get('date_from'):
            domain.append(('date_reception', '>=', params['date_from']))

        missions = request.env['sinistre.mission'].sudo().search(domain, limit=100, order='date_reception desc')

        return _json_response({
            'success': True,
            'count': len(missions),
            'missions': [{
                'reference': m.reference,
                'ref_assurance': m.ref_assurance,
                'state': m.state,
                'type_intervention': m.type_intervention,
                'date_reception': str(m.date_reception),
                'client': m.client_id.name,
                'adresse': m.adresse_intervention,
            } for m in missions],
        })

    # ─── DEMANDE DIRECTE PARTICULIER / PRO ───────────────────────────
    @http.route('/api/sinistre/v1/demande', type='http', auth='public', methods=['POST'], csrf=False)
    def creer_demande_directe(self, **kwargs):
        """
        Crée une demande d'intervention directe (sans assurance).
        Accessible depuis le formulaire web ou l'application.

        Body JSON :
        {
            "source": "particulier",  // particulier|entreprise
            "type_intervention": "plomberie",
            "urgence": "normale",
            "description": "Fuite sous évier cuisine",
            "client": {
                "nom": "Martin",
                "prenom": "Sophie",
                "email": "sophie@email.fr",
                "tel": "0612341234",
                "is_company": false
            },
            "adresse_intervention": "5 avenue Victor Hugo, 75016 Paris"
        }
        """
        try:
            body = json.loads(request.httprequest.data.decode('utf-8'))
        except Exception as e:
            return _json_error(400, "Body JSON invalide", str(e))

        required = ['type_intervention', 'description', 'adresse_intervention', 'client']
        missing = [f for f in required if not body.get(f)]
        if missing:
            return _json_error(400, f"Champs obligatoires : {', '.join(missing)}")

        client_data = body.get('client', {})
        env = request.env(su=True)
        partner = _find_or_create_partner(env, client_data)

        source = body.get('source', 'particulier')
        if source not in ('particulier', 'entreprise'):
            source = 'particulier'

        try:
            mission = env['sinistre.mission'].create({
                'source': source,
                'client_id': partner.id,
                'type_intervention': body.get('type_intervention', 'autre'),
                'urgence': body.get('urgence', 'normale'),
                'description_sinistre': body.get('description', ''),
                'adresse_intervention': body.get('adresse_intervention', ''),
                'contact_sur_place': body.get('contact_sur_place', ''),
                'tel_sur_place': body.get('tel_sur_place', ''),
            })

            return _json_response({
                'success': True,
                'reference': mission.reference,
                'token': mission.token_api,
                'message': 'Demande enregistrée, nous vous contacterons rapidement.',
            }, status=201)

        except Exception as e:
            _logger.error(f"Erreur création demande directe: {e}")
            return _json_error(500, "Erreur interne", str(e))

    # ─── API PWA INTERVENANT ──────────────────────────────────────────
    @http.route('/api/sinistre/v1/intervenant/missions', type='http', auth='user', methods=['GET'], csrf=False)
    def mes_missions(self, **kwargs):
        """Retourne les missions assignées à l'intervenant connecté."""
        user = request.env.user
        intervenant = request.env['sinistre.intervenant'].search([('user_id', '=', user.id)], limit=1)
        if not intervenant:
            return _json_error(403, "Aucun intervenant associé à ce compte")

        missions = request.env['sinistre.mission'].search([
            ('intervenant_id', '=', intervenant.id),
            ('state', 'not in', ('clos', 'annule')),
        ], order='urgence desc, date_rdv asc')

        return _json_response({
            'success': True,
            'missions': [{
                'id': m.id,
                'reference': m.reference,
                'state': m.state,
                'type_intervention': m.type_intervention,
                'urgence': m.urgence,
                'adresse': m.adresse_intervention,
                'client': m.client_id.name,
                'tel_sur_place': m.tel_sur_place or '',
                'date_rdv': str(m.date_rdv) if m.date_rdv else None,
                'description': m.description_sinistre,
                'photos_avant': m.photos_avant_count,
                'photos_apres': m.photos_apres_count,
                'montant_devis': m.montant_devis,
                'reste_a_charge': m.reste_a_charge,
            } for m in missions],
        })


# ─── Helpers ─────────────────────────────────────────────────────────────────

def _find_or_create_partner(env, client_data):
    """Trouve ou crée un partenaire Odoo à partir des données client."""
    email = client_data.get('email', '')
    partner = None

    if email:
        partner = env['res.partner'].search([('email', '=', email)], limit=1)

    if not partner:
        is_company = client_data.get('is_company', False)
        nom = client_data.get('nom', '')
        prenom = client_data.get('prenom', '')
        name = f"{prenom} {nom}".strip() if not is_company else nom

        partner = env['res.partner'].create({
            'name': name or 'Client Inconnu',
            'email': email,
            'phone': client_data.get('tel', ''),
            'is_company': is_company,
        })

    return partner
