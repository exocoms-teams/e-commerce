# -*- coding: utf-8 -*-
"""
api_pwa.py — Endpoints API complémentaires pour la PWA Intervenant
À ajouter dans sinistre_services/controllers/

Endpoints :
  GET  /api/sinistre/v1/intervenant/missions          → Liste missions (existant)
  GET  /api/sinistre/v1/mission/<ref>                 → Détail mission avec photos + devis
  POST /api/sinistre/v1/intervenant/mission/<id>/demarrer
  POST /api/sinistre/v1/intervenant/mission/<id>/terminer
  POST /api/sinistre/v1/intervenant/mission/<id>/devis
  POST /api/sinistre/v1/intervenant/devis/<id>/envoyer
  POST /api/sinistre/v1/intervenant/devis/<id>/accepter
  POST /api/sinistre/v1/intervenant/devis/<id>/refuser
  POST /api/sinistre/v1/intervenant/mission/<id>/photo
  POST /api/sinistre/v1/intervenant/fcm-token
"""
import json
import base64
import logging

from odoo import http, _
from odoo.http import request, Response

_logger = logging.getLogger(__name__)


def _json_response(data, status=200):
    return Response(
        json.dumps(data, default=str, ensure_ascii=False),
        status=status,
        content_type='application/json; charset=utf-8',
    )

def _json_error(status, message):
    return _json_response({'success': False, 'error': message}, status=status)

def _get_intervenant():
    """Retourne l'intervenant lié à l'utilisateur connecté."""
    user = request.env.user
    if user._is_public():
        return None
    return request.env['sinistre.intervenant'].search([('user_id', '=', user.id)], limit=1)


class SinistrePWAController(http.Controller):

    # ─── DÉTAIL COMPLET D'UNE MISSION ───────────────────────────────
    @http.route('/api/sinistre/v1/mission/<string:reference>', type='http',
                auth='user', methods=['GET'], csrf=False)
    def get_mission_detail(self, reference, **kwargs):
        """Retourne la mission avec photos, devis et contexte financier."""
        intervenant = _get_intervenant()
        if not intervenant:
            return _json_error(403, "Accès non autorisé")

        domain = [('intervenant_id', '=', intervenant.id)]
        # Recherche par id (int) ou par reference (str)
        if reference.isdigit():
            domain.append(('id', '=', int(reference)))
        else:
            domain.append(('reference', '=', reference))

        mission = request.env['sinistre.mission'].search(domain, limit=1)
        if not mission:
            return _json_error(404, "Mission introuvable")

        # Photos
        photos = [{
            'id':        p.id,
            'type_photo':p.type_photo,
            'description':p.description or '',
            'date':      str(p.date_prise),
            'url':       f'/web/image/sinistre.photo/{p.id}/image',
        } for p in mission.photo_ids]

        # Devis
        devis_data = None
        if mission.devis_ids:
            devis = mission.devis_ids.sorted('date_devis', reverse=True)[0]
            devis_data = {
                'id':           devis.id,
                'name':         devis.name,
                'state':        devis.state,
                'montant_ht':   devis.montant_ht,
                'montant_total':devis.montant_total,
                'lignes': [{
                    'description':   l.description,
                    'quantite':      l.quantite,
                    'prix_unitaire': l.prix_unitaire,
                    'montant_total': l.montant_total,
                } for l in devis.ligne_ids],
            }

        return _json_response({
            'success': True,
            'mission': {
                'id':              mission.id,
                'reference':       mission.reference,
                'state':           mission.state,
                'source':          mission.source,
                'type_intervention':mission.type_intervention,
                'urgence':         mission.urgence,
                'description':     mission.description_sinistre,
                'adresse':         mission.adresse_intervention,
                'client':          mission.client_id.name if mission.client_id else '',
                'tel_sur_place':   mission.tel_sur_place or '',
                'contact_sur_place':mission.contact_sur_place or '',
                'date_rdv':        str(mission.date_rdv) if mission.date_rdv else None,
                'montant_devis':   mission.montant_devis,
                'reste_a_charge':  mission.reste_a_charge,
                'photos_avant':    mission.photos_avant_count,
                'photos_apres':    mission.photos_apres_count,
                'photos':          photos,
                'devis':           devis_data,
            }
        })

    # ─── DÉMARRER LES TRAVAUX ───────────────────────────────────────
    @http.route('/api/sinistre/v1/intervenant/mission/<int:mission_id>/demarrer',
                type='http', auth='user', methods=['POST'], csrf=False)
    def demarrer_mission(self, mission_id, **kwargs):
        intervenant = _get_intervenant()
        if not intervenant:
            return _json_error(403, "Accès non autorisé")

        mission = request.env['sinistre.mission'].search([
            ('id', '=', mission_id), ('intervenant_id', '=', intervenant.id)
        ], limit=1)
        if not mission:
            return _json_error(404, "Mission introuvable")

        try:
            mission.action_demarrer()
            return _json_response({'success': True, 'state': mission.state})
        except Exception as e:
            return _json_error(400, str(e))

    # ─── TERMINER LA MISSION ────────────────────────────────────────
    @http.route('/api/sinistre/v1/intervenant/mission/<int:mission_id>/terminer',
                type='http', auth='user', methods=['POST'], csrf=False)
    def terminer_mission(self, mission_id, **kwargs):
        intervenant = _get_intervenant()
        if not intervenant:
            return _json_error(403, "Accès non autorisé")

        mission = request.env['sinistre.mission'].search([
            ('id', '=', mission_id), ('intervenant_id', '=', intervenant.id)
        ], limit=1)
        if not mission:
            return _json_error(404, "Mission introuvable")

        try:
            mission.action_terminer()
            return _json_response({'success': True, 'state': mission.state})
        except Exception as e:
            return _json_error(400, str(e))

    # ─── CRÉER UN DEVIS ─────────────────────────────────────────────
    @http.route('/api/sinistre/v1/intervenant/mission/<int:mission_id>/devis',
                type='http', auth='user', methods=['POST'], csrf=False)
    def creer_devis(self, mission_id, **kwargs):
        intervenant = _get_intervenant()
        if not intervenant:
            return _json_error(403, "Accès non autorisé")

        mission = request.env['sinistre.mission'].search([
            ('id', '=', mission_id), ('intervenant_id', '=', intervenant.id)
        ], limit=1)
        if not mission:
            return _json_error(404, "Mission introuvable")

        try:
            body = json.loads(request.httprequest.data.decode('utf-8'))
        except Exception:
            return _json_error(400, "Body JSON invalide")

        lignes = body.get('ligne_ids', [])
        if not lignes:
            return _json_error(400, "Au moins une ligne est requise")

        try:
            env = request.env
            devis = env['sinistre.devis'].create({
                'mission_id': mission.id,
                'note_client': body.get('note_client', ''),
                'tva': body.get('tva', 20.0),
                'ligne_ids': [(0, 0, {
                    'description':   l['description'],
                    'quantite':      float(l.get('quantite', 1)),
                    'prix_unitaire': float(l.get('prix_unitaire', 0)),
                    'unite':         l.get('unite', 'forfait'),
                }) for l in lignes],
            })
            return _json_response({
                'success': True,
                'devis_id': devis.id,
                'name': devis.name,
                'montant_total': devis.montant_total,
            }, status=201)
        except Exception as e:
            return _json_error(500, str(e))

    # ─── ENVOYER LE DEVIS ───────────────────────────────────────────
    @http.route('/api/sinistre/v1/intervenant/devis/<int:devis_id>/envoyer',
                type='http', auth='user', methods=['POST'], csrf=False)
    def envoyer_devis(self, devis_id, **kwargs):
        intervenant = _get_intervenant()
        if not intervenant:
            return _json_error(403, "Accès non autorisé")

        devis = request.env['sinistre.devis'].search([
            ('id', '=', devis_id),
            ('intervenant_id', '=', intervenant.id),
        ], limit=1)
        if not devis:
            return _json_error(404, "Devis introuvable")

        try:
            devis.action_envoyer()
            return _json_response({'success': True, 'state': devis.state})
        except Exception as e:
            return _json_error(400, str(e))

    # ─── ACCEPTER LE DEVIS (signature) ──────────────────────────────
    @http.route('/api/sinistre/v1/intervenant/devis/<int:devis_id>/accepter',
                type='http', auth='user', methods=['POST'], csrf=False)
    def accepter_devis(self, devis_id, **kwargs):
        intervenant = _get_intervenant()
        if not intervenant:
            return _json_error(403, "Accès non autorisé")

        devis = request.env['sinistre.devis'].search([
            ('id', '=', devis_id), ('intervenant_id', '=', intervenant.id)
        ], limit=1)
        if not devis:
            return _json_error(404, "Devis introuvable")

        try:
            body = json.loads(request.httprequest.data.decode('utf-8'))
        except Exception:
            body = {}

        signature_b64 = body.get('signature', '')

        try:
            devis.write({'signature_client': signature_b64 or False})
            devis.action_accepter()
            return _json_response({'success': True, 'state': devis.state})
        except Exception as e:
            return _json_error(400, str(e))

    # ─── REFUSER LE DEVIS ───────────────────────────────────────────
    @http.route('/api/sinistre/v1/intervenant/devis/<int:devis_id>/refuser',
                type='http', auth='user', methods=['POST'], csrf=False)
    def refuser_devis(self, devis_id, **kwargs):
        intervenant = _get_intervenant()
        if not intervenant:
            return _json_error(403, "Accès non autorisé")

        devis = request.env['sinistre.devis'].search([
            ('id', '=', devis_id), ('intervenant_id', '=', intervenant.id)
        ], limit=1)
        if not devis:
            return _json_error(404, "Devis introuvable")

        try:
            devis.action_refuser()
            return _json_response({'success': True, 'state': devis.state})
        except Exception as e:
            return _json_error(400, str(e))

    # ─── UPLOAD PHOTO ───────────────────────────────────────────────
    @http.route('/api/sinistre/v1/intervenant/mission/<int:mission_id>/photo',
                type='http', auth='user', methods=['POST'], csrf=False)
    def upload_photo(self, mission_id, **kwargs):
        intervenant = _get_intervenant()
        if not intervenant:
            return _json_error(403, "Accès non autorisé")

        mission = request.env['sinistre.mission'].search([
            ('id', '=', mission_id), ('intervenant_id', '=', intervenant.id)
        ], limit=1)
        if not mission:
            return _json_error(404, "Mission introuvable")

        try:
            body = json.loads(request.httprequest.data.decode('utf-8'))
        except Exception:
            return _json_error(400, "Body JSON invalide")

        image_b64   = body.get('image', '')
        type_photo  = body.get('type_photo', 'avant')
        description = body.get('description', '')

        if not image_b64:
            return _json_error(400, "Image base64 requise")

        if type_photo not in ('avant', 'pendant', 'apres'):
            type_photo = 'avant'

        try:
            photo = request.env['sinistre.photo'].create({
                'mission_id':  mission.id,
                'type_photo':  type_photo,
                'image':       image_b64,
                'description': description,
                'intervenant_id': intervenant.id,
            })
            return _json_response({
                'success': True,
                'photo_id': photo.id,
                'type_photo': type_photo,
                'url': f'/web/image/sinistre.photo/{photo.id}/image',
            }, status=201)
        except Exception as e:
            _logger.error(f"Photo upload error: {e}")
            return _json_error(500, str(e))

    # ─── SAUVEGARDER TOKEN FCM ──────────────────────────────────────
    @http.route('/api/sinistre/v1/intervenant/fcm-token',
                type='http', auth='user', methods=['POST'], csrf=False)
    def save_fcm_token(self, **kwargs):
        intervenant = _get_intervenant()
        if not intervenant:
            return _json_error(403, "Accès non autorisé")

        try:
            body  = json.loads(request.httprequest.data.decode('utf-8'))
            token = body.get('token', '').strip()
        except Exception:
            return _json_error(400, "Body JSON invalide")

        if not token:
            return _json_error(400, "Token FCM requis")

        # Sauvegarder sur l'intervenant (champ à ajouter au modèle)
        intervenant.write({'fcm_token': token})
        return _json_response({'success': True, 'message': 'Token FCM enregistré'})
