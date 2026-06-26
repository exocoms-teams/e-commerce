# -*- coding: utf-8 -*-
"""
api_assurance.py — API REST pour les compagnies d'assurance
Auth : clé API dans le header X-API-Key
"""
import json
import logging
from odoo import http, fields
from odoo.http import request, Response

_logger = logging.getLogger(__name__)


def _ok(data, status=200):
    return Response(
        json.dumps(data, default=str, ensure_ascii=False),
        status=status, content_type='application/json; charset=utf-8',
    )

def _err(status, msg):
    return _ok({'success': False, 'error': msg}, status=status)

def _auth_assurance():
    """Retourne la compagnie d'assurance authentifiée via X-API-Key."""
    key = request.httprequest.headers.get('X-API-Key', '')
    if not key:
        return None
    return request.env['sinistre.assurance'].sudo().search(
        [('api_key', '=', key), ('api_key_active', '=', True), ('statut_compte', '=', 'actif')],
        limit=1
    )


class AssuranceAPIController(http.Controller):

    # ── PING ─────────────────────────────────────────────────────────
    @http.route('/api/assurance/v1/ping', type='http', auth='public', methods=['GET'], csrf=False)
    def ping(self, **kw):
        return _ok({'success': True, 'status': 'ok'})

    # ── CRÉER ORDRE DE MISSION ────────────────────────────────────────
    @http.route('/api/assurance/v1/mission', type='http', auth='public', methods=['POST'], csrf=False)
    def create_mission(self, **kw):
        assurance = _auth_assurance()
        if not assurance:
            return _err(401, "Clé API invalide ou compte inactif")
        try:
            data = json.loads(request.httprequest.data or '{}')

            # Client / assuré
            email = data.get('client_email', '')
            partner = request.env['res.partner'].sudo().search([('email', '=', email)], limit=1) if email else None
            if not partner:
                partner = request.env['res.partner'].sudo().create({
                    'name':  data.get('client_nom', 'Assuré'),
                    'email': email,
                    'phone': data.get('client_tel', ''),
                    'street': data.get('adresse', ''),
                })

            mission = request.env['sinistre.mission'].sudo().create({
                'source':               'assurance',
                'assurance_id':         assurance.id,
                'ref_assurance':        data.get('ref_assurance', ''),
                'contrat_assurance':    data.get('num_contrat', ''),
                'client_id':            partner.id,
                'type_intervention':    data.get('type_intervention', 'autre'),
                'urgence':              data.get('urgence', 'normale'),
                'description_sinistre': data.get('description', ''),
                'adresse_intervention': data.get('adresse', ''),
                'tel_sur_place':        data.get('client_tel', ''),
                'montant_garanti':      float(data.get('montant_garanti', 0)),
                'franchise':            float(data.get('franchise', 0)),
            })

            return _ok({
                'success':    True,
                'reference':  mission.reference,
                'id':         mission.id,
                'state':      mission.state,
            }, status=201)

        except Exception as e:
            _logger.error(f"[assurance API] create_mission: {e}")
            return _err(500, str(e))

    # ── LISTE MES MISSIONS ────────────────────────────────────────────
    @http.route('/api/assurance/v1/missions', type='http', auth='public', methods=['GET'], csrf=False)
    def list_missions(self, **kw):
        assurance = _auth_assurance()
        if not assurance:
            return _err(401, "Clé API invalide")
        missions = request.env['sinistre.mission'].sudo().search(
            [('assurance_id', '=', assurance.id)],
            order='date_reception desc', limit=100,
        )
        return _ok({'success': True, 'missions': [_fmt(m) for m in missions], 'total': len(missions)})

    # ── DÉTAIL MISSION ────────────────────────────────────────────────
    @http.route('/api/assurance/v1/mission/<string:ref>', type='http', auth='public', methods=['GET'], csrf=False)
    def get_mission(self, ref, **kw):
        assurance = _auth_assurance()
        if not assurance:
            return _err(401, "Clé API invalide")
        m = request.env['sinistre.mission'].sudo().search(
            [('assurance_id', '=', assurance.id), ('reference', '=', ref)], limit=1
        ) or request.env['sinistre.mission'].sudo().search(
            [('assurance_id', '=', assurance.id), ('ref_assurance', '=', ref)], limit=1
        )
        if not m:
            return _err(404, "Mission introuvable")
        data = _fmt(m)
        # Messages
        data['messages'] = [{
            'auteur':    msg.auteur_nom or msg.auteur_type,
            'contenu':   msg.contenu,
            'date':      str(msg.date_envoi),
        } for msg in m.sinistre_message_ids]
        # Devis
        data['devis'] = [{
            'id':            d.id,
            'state':         d.state,
            'montant_total': d.montant_total,
        } for d in m.devis_ids]
        return _ok({'success': True, 'mission': data})

    # ── ANNULER MISSION ───────────────────────────────────────────────
    @http.route('/api/assurance/v1/mission/<string:ref>/annuler', type='http',
                auth='public', methods=['POST'], csrf=False)
    def annuler_mission(self, ref, **kw):
        assurance = _auth_assurance()
        if not assurance:
            return _err(401, "Clé API invalide")
        m = request.env['sinistre.mission'].sudo().search(
            [('assurance_id', '=', assurance.id), ('reference', '=', ref)], limit=1
        )
        if not m:
            return _err(404, "Mission introuvable")
        if m.state in ('termine', 'facture', 'clos', 'annule'):
            return _err(400, f"Impossible d'annuler une mission en état '{m.state}'")

        data   = json.loads(request.httprequest.data or '{}')
        motif  = data.get('motif', 'assurance_annule')
        artisan_sur_place = data.get('artisan_sur_place', False)
        frais  = float(data.get('frais_deplacement', 0))

        # Vérifier délai d'annulation
        ok, delta = assurance._check_annulation_autorisee(m)
        facturer = artisan_sur_place or (not ok)

        m.write({
            'motif_annulation':          motif,
            'annule_par':                'assurance',
            'artisan_sur_place':         artisan_sur_place,
            'facturer_deplacement':      facturer,
            'frais_deplacement':         frais if facturer else 0,
            'facturation_deplacement_a': 'assurance',
        })
        m.action_annuler()

        # Message sur la mission
        request.env['sinistre.message'].sudo().create({
            'mission_id':  m.id,
            'auteur_type': 'assurance',
            'auteur_nom':  assurance.name,
            'contenu':     f"Mission annulée par l'assurance. Motif : {motif}."
                           + (f" Frais déplacement : {frais} €" if facturer else ""),
        })

        return _ok({
            'success':              True,
            'reference':            m.reference,
            'state':                'annule',
            'frais_deplacement':    frais if facturer else 0,
            'factures_a':           'assurance' if facturer else None,
        })

    # ── ENVOYER MESSAGE ───────────────────────────────────────────────
    @http.route('/api/assurance/v1/mission/<string:ref>/message', type='http',
                auth='public', methods=['POST'], csrf=False)
    def send_message(self, ref, **kw):
        assurance = _auth_assurance()
        if not assurance:
            return _err(401, "Clé API invalide")
        m = request.env['sinistre.mission'].sudo().search(
            [('assurance_id', '=', assurance.id), ('reference', '=', ref)], limit=1
        )
        if not m:
            return _err(404, "Mission introuvable")
        data = json.loads(request.httprequest.data or '{}')
        msg  = request.env['sinistre.message'].sudo().create({
            'mission_id':  m.id,
            'auteur_type': 'assurance',
            'auteur_nom':  assurance.name,
            'contenu':     data.get('message', ''),
        })
        return _ok({'success': True, 'message_id': msg.id, 'date': str(msg.date_envoi)})

    # ── INSCRIPTION ASSURANCE ─────────────────────────────────────────
    @http.route('/api/assurance/v1/inscription', type='http', auth='public', methods=['POST'], csrf=False)
    def inscription(self, **kw):
        """Inscription d'une nouvelle compagnie d'assurance."""
        try:
            data = json.loads(request.httprequest.data or '{}')
            nom   = data.get('nom', '')
            email = data.get('email', '')
            tel   = data.get('telephone', '')
            siret = data.get('siret', '')
            if not nom or not email:
                return _err(400, "Nom et email obligatoires")

            # Vérifier doublon
            existing = request.env['sinistre.assurance'].sudo().search([
                ('partner_id.email', '=', email)
            ], limit=1)
            if existing:
                return _err(409, "Une compagnie avec cet email existe déjà")

            partner = request.env['res.partner'].sudo().create({
                'name':    nom,
                'email':   email,
                'phone':   tel,
                'company_type': 'company',
            })
            assurance = request.env['sinistre.assurance'].sudo().create({
                'name':           nom,
                'partner_id':     partner.id,
                'statut_compte':  'en_attente',
                'note':           f"SIRET: {siret}" if siret else '',
            })
            return _ok({
                'success': True,
                'message': "Inscription reçue — en attente de validation par la plateforme",
                'id':      assurance.id,
            }, status=201)
        except Exception as e:
            return _err(500, str(e))


def _fmt(m):
    return {
        'id':                  m.id,
        'reference':           m.reference,
        'ref_assurance':       m.ref_assurance or '',
        'state':               m.state,
        'type_intervention':   m.type_intervention,
        'urgence':             m.urgence,
        'client':              m.client_id.name if m.client_id else '',
        'adresse':             m.adresse_intervention or '',
        'date_rdv':            str(m.date_rdv) if m.date_rdv else None,
        'description':         m.description_sinistre or '',
        'montant_garanti':     m.montant_garanti or 0,
        'franchise':           m.franchise or 0,
        'montant_devis':       m.montant_devis or 0,
        'intervenant':         m.intervenant_id.name if m.intervenant_id else None,
        'date_reception':      str(m.date_reception) if m.date_reception else None,
        'date_cloture':        str(m.date_cloture) if m.date_cloture else None,
    }
