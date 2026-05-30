# -*- coding: utf-8 -*-
"""
api_controller.py — API REST pour la PWA Intervenant
"""
import json
import logging

from odoo import http
from odoo.http import request, Response

_logger = logging.getLogger(__name__)


def _ok(data, status=200):
    return Response(
        json.dumps(data, default=str, ensure_ascii=False),
        status=status,
        content_type='application/json; charset=utf-8',
        headers=[('Access-Control-Allow-Origin', '*')],
    )

def _err(status, message, detail=None):
    return _ok({'success': False, 'error': message, 'detail': detail}, status=status)


class SinistreAPIController(http.Controller):

    # ── PING ─────────────────────────────────────────────────────────
    @http.route('/api/sinistre/v1/ping', type='http', auth='public', methods=['GET'], csrf=False)
    def ping(self, **kw):
        return _ok({'success': True, 'status': 'ok'})

    # ── SESSION INFO (pour récupérer nom/email côté PWA) ─────────────
    @http.route('/api/sinistre/v1/me', type='http', auth='user', methods=['GET'], csrf=False)
    def me(self, **kw):
        """Retourne les infos de l'utilisateur connecté + son intervenant."""
        user = request.env.user
        interv = request.env['sinistre.intervenant'].sudo().search(
            [('user_id', '=', user.id)], limit=1
        )

        # Auto-création de la fiche intervenant si absente
        if not interv:
            partner = user.partner_id
            interv = request.env['sinistre.intervenant'].sudo().create({
                'name':            user.name,
                'partner_id':      partner.id,
                'user_id':         user.id,
                'taux_commission': 15.0,
                'disponible':      True,
                'actif':           True,
            })
            _logger.info(f"[sinistre] Intervenant auto-créé pour {user.login}")

        # Stats
        missions = request.env['sinistre.mission'].sudo().search(
            [('intervenant_id', '=', interv.id)]
        )
        total = len(missions)
        ca = sum(m.montant_devis or 0 for m in missions if m.state in ('termine', 'clos', 'facture'))

        return _ok({
            'success': True,
            'user': {
                'uid':           user.id,
                'name':          user.name,
                'email':         user.login,
                'company_name':  interv.name or user.name,
                'zone':          interv.zone_intervention or 'Paris',
                'note_moyenne':  4.9,
                'interventions': total,
                'ca_total':      ca,
                'disponible':    interv.disponible,
                'intervenant_id': interv.id,
            }
        })

    # ── MES MISSIONS ─────────────────────────────────────────────────
    @http.route('/api/sinistre/v1/intervenant/missions', type='http',
                auth='user', methods=['GET'], csrf=False)
    def mes_missions(self, **kw):
        user = request.env.user
        interv = request.env['sinistre.intervenant'].sudo().search(
            [('user_id', '=', user.id)], limit=1
        )

        # Auto-création si absent
        if not interv:
            interv = request.env['sinistre.intervenant'].sudo().create({
                'name':            user.name,
                'partner_id':      user.partner_id.id,
                'user_id':         user.id,
                'taux_commission': 15.0,
                'disponible':      True,
                'actif':           True,
            })
            _logger.info(f"[sinistre] Intervenant auto-créé pour {user.login}")

        missions = request.env['sinistre.mission'].sudo().search([
            ('intervenant_id', '=', interv.id),
            ('state', 'not in', ('clos', 'annule')),
        ], order='urgence desc, date_rdv asc')

        def _fmt_mission(m):
            return {
                'id':               m.id,
                'reference':        m.reference,
                'state':            m.state,
                'type_intervention':m.type_intervention,
                'urgence':          m.urgence,
                'adresse':          m.adresse_intervention or '',
                'adresse_intervention': m.adresse_intervention or '',
                'client':           m.client_id.name if m.client_id else '',
                'tel_sur_place':    m.tel_sur_place or '',
                'date_rdv':         str(m.date_rdv) if m.date_rdv else None,
                'description':      m.description_sinistre or '',
                'description_sinistre': m.description_sinistre or '',
                'montant':          m.montant_devis or 0,
                'montant_devis':    m.montant_devis or 0,
                'reste_a_charge':   m.reste_a_charge or 0,
                'photos_avant':     m.photos_avant_count if hasattr(m, 'photos_avant_count') else 0,
                'photos_apres':     m.photos_apres_count if hasattr(m, 'photos_apres_count') else 0,
            }

        return _ok({
            'success':  True,
            'missions': [_fmt_mission(m) for m in missions],
            'total':    len(missions),
        })

    # ── DÉTAIL MISSION ───────────────────────────────────────────────
    @http.route('/api/sinistre/v1/mission/<string:reference>', type='http',
                auth='user', methods=['GET'], csrf=False)
    def get_mission_detail(self, reference, **kw):
        user = request.env.user
        interv = request.env['sinistre.intervenant'].sudo().search(
            [('user_id', '=', user.id)], limit=1
        )
        if not interv:
            return _err(403, "Aucun intervenant associé à ce compte")

        domain = [('intervenant_id', '=', interv.id)]
        if reference.isdigit():
            domain.append(('id', '=', int(reference)))
        else:
            domain.append(('reference', '=', reference))

        mission = request.env['sinistre.mission'].sudo().search(domain, limit=1)
        if not mission:
            return _err(404, "Mission introuvable")

        photos = [{
            'id':         p.id,
            'type_photo': p.type_photo,
            'description':p.description or '',
            'url':        f'/web/image/sinistre.photo/{p.id}/image',
        } for p in (mission.photo_ids if hasattr(mission, 'photo_ids') else [])]

        devis_data = None
        if hasattr(mission, 'devis_ids') and mission.devis_ids:
            devis = mission.devis_ids.sorted('id', reverse=True)[0]
            devis_data = {
                'id':           devis.id,
                'state':        devis.state,
                'montant_total':devis.montant_total,
                'lignes': [{
                    'description':   l.description,
                    'quantite':      l.quantite,
                    'prix_unitaire': l.prix_unitaire,
                    'montant_total': l.montant_total,
                } for l in (devis.ligne_ids if hasattr(devis, 'ligne_ids') else [])],
            }

        return _ok({
            'success': True,
            'mission': {
                'id':               mission.id,
                'reference':        mission.reference,
                'state':            mission.state,
                'type_intervention':mission.type_intervention,
                'urgence':          mission.urgence,
                'source':           mission.source if hasattr(mission, 'source') else '',
                'client':           mission.client_id.name if mission.client_id else '',
                'tel_sur_place':    mission.tel_sur_place or '',
                'adresse':          mission.adresse_intervention or '',
                'date_rdv':         str(mission.date_rdv) if mission.date_rdv else None,
                'description':      mission.description_sinistre or '',
                'montant_devis':    mission.montant_devis or 0,
                'reste_a_charge':   mission.reste_a_charge or 0,
                'photos':           photos,
                'devis':            devis_data,
            }
        })

    # ── DÉMARRER ─────────────────────────────────────────────────────
    @http.route('/api/sinistre/v1/intervenant/mission/<int:mission_id>/demarrer',
                type='http', auth='user', methods=['POST'], csrf=False)
    def demarrer_mission(self, mission_id, **kw):
        try:
            mission = request.env['sinistre.mission'].sudo().browse(mission_id)
            if not mission.exists():
                return _err(404, "Mission introuvable")
            mission.write({'state': 'en_cours'})
            return _ok({'success': True, 'state': 'en_cours'})
        except Exception as e:
            return _err(500, str(e))

    # ── TERMINER ─────────────────────────────────────────────────────
    @http.route('/api/sinistre/v1/intervenant/mission/<int:mission_id>/terminer',
                type='http', auth='user', methods=['POST'], csrf=False)
    def terminer_mission(self, mission_id, **kw):
        try:
            mission = request.env['sinistre.mission'].sudo().browse(mission_id)
            if not mission.exists():
                return _err(404, "Mission introuvable")
            from odoo.fields import Datetime
            mission.write({'state': 'termine', 'date_cloture': Datetime.now()})
            return _ok({'success': True, 'state': 'termine'})
        except Exception as e:
            return _err(500, str(e))

    # ── FCM TOKEN ────────────────────────────────────────────────────
    @http.route('/api/sinistre/v1/intervenant/fcm-token', type='http',
                auth='user', methods=['POST'], csrf=False)
    def save_fcm_token(self, **kw):
        try:
            data = json.loads(request.httprequest.data or '{}')
            token = data.get('token', '')
            user = request.env.user
            interv = request.env['sinistre.intervenant'].sudo().search(
                [('user_id', '=', user.id)], limit=1
            )
            if interv and token:
                interv.write({'fcm_token': token})
            return _ok({'success': True})
        except Exception as e:
            return _err(500, str(e))

    # ── DEMANDE PUBLIQUE ─────────────────────────────────────────────
    @http.route('/api/sinistre/v1/mission', type='http', auth='public',
                methods=['POST'], csrf=False)
    def create_mission(self, **kw):
        try:
            data = json.loads(request.httprequest.data or '{}')
            partner = _get_or_create_partner(request.env, data)
            mission = request.env['sinistre.mission'].sudo().create({
                'source':               data.get('source', 'particulier'),
                'client_id':            partner.id,
                'type_intervention':    data.get('type_intervention', 'autre'),
                'urgence':              data.get('urgence', 'normale'),
                'description_sinistre': data.get('description', ''),
                'adresse_intervention': data.get('adresse', ''),
                'tel_sur_place':        data.get('tel', ''),
            })
            return _ok({'success': True, 'reference': mission.reference, 'id': mission.id})
        except Exception as e:
            _logger.error(f"[sinistre] Erreur création mission: {e}")
            return _err(500, str(e))


def _get_or_create_partner(env, data):
    email = data.get('email', '')
    partner = env['res.partner'].sudo().search([('email', '=', email)], limit=1) if email else None
    if not partner:
        nom = data.get('nom', data.get('name', 'Client'))
        partner = env['res.partner'].sudo().create({
            'name':  nom,
            'email': email,
            'phone': data.get('tel', ''),
        })
    return partner
