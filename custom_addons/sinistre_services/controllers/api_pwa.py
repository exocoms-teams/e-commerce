# -*- coding: utf-8 -*-
import json
import logging

from odoo import http, _
from odoo.http import request, Response

_logger = logging.getLogger(__name__)


def _json_response(data, status=200):
    return Response(
        json.dumps(data, default=str, ensure_ascii=False),
        status=status, content_type='application/json; charset=utf-8',
    )

def _json_error(status, message):
    return _json_response({'success': False, 'error': message}, status=status)

def _get_intervenant():
    """Retourne l'intervenant lié à l'utilisateur connecté, le crée si absent."""
    user = request.env.user
    if user._is_public():
        return None
    iv = request.env['sinistre.intervenant'].sudo().search(
        [('user_id', '=', user.id)], limit=1
    )
    if not iv:
        iv = request.env['sinistre.intervenant'].sudo().create({
            'name':            user.name,
            'partner_id':      user.partner_id.id,
            'user_id':         user.id,
            'taux_commission': 15.0,
            'disponible':      True,
            'actif':           True,
        })
    return iv

def _check_mission(intervenant, mission_id):
    """Retourne la mission si accessible à cet intervenant, None sinon."""
    return request.env['sinistre.mission'].sudo().search([
        ('id', '=', mission_id),
        ('intervenant_id', '=', intervenant.id),
    ], limit=1)


class SinistrePWAController(http.Controller):

    # ─── DÉTAIL COMPLET D'UNE MISSION ───────────────────────────────
    @http.route('/api/sinistre/v1/mission/<string:reference>',
                type='http', auth='user', methods=['GET'], csrf=False)
    def get_mission_detail(self, reference, **kwargs):
        intervenant = _get_intervenant()
        if not intervenant:
            return _json_error(403, "Accès non autorisé")

        domain = [('intervenant_id', '=', intervenant.id)]
        if reference.isdigit():
            domain.append(('id', '=', int(reference)))
        else:
            domain.append(('reference', '=', reference))

        mission = request.env['sinistre.mission'].sudo().search(domain, limit=1)
        if not mission:
            return _json_error(404, "Mission introuvable")

        photos = [{
            'id':          p.id,
            'type_photo':  p.type_photo,
            'description': p.description or '',
            'date':        str(p.date_prise),
            'url':         f'/web/image/sinistre.photo/{p.id}/image',
        } for p in mission.photo_ids]

        devis_data = None
        if mission.devis_ids:
            devis = mission.devis_ids.sorted('date_devis', reverse=True)[0]
            devis_data = {
                'id':            devis.id,
                'name':          devis.name,
                'state':         devis.state,
                'montant_ht':    devis.montant_ht,
                'montant_total': devis.montant_total,
                'note_client':   devis.note_client or '',
                'lignes': [{
                    'id':            l.id,
                    'description':   l.description,
                    'quantite':      l.quantite,
                    'prix_unitaire': l.prix_unitaire,
                    'montant_total': l.montant_total,
                } for l in devis.ligne_ids],
            }

        unread = request.env['sinistre.message'].sudo().search_count([
            ('mission_id', '=', mission.id),
            ('auteur_type', '!=', 'artisan'),
            ('lu_artisan', '=', False),
        ])

        return _json_response({
            'success': True,
            'mission': {
                'id':                mission.id,
                'reference':         mission.reference,
                'state':             mission.state,
                'source':            mission.source,
                'type_intervention': mission.type_intervention,
                'urgence':           mission.urgence,
                'description':       mission.description_sinistre,
                'adresse':           mission.adresse_intervention,
                'client':            mission.client_id.name if mission.client_id else '',
                'tel_sur_place':     mission.tel_sur_place or '',
                'contact_sur_place': mission.contact_sur_place or '',
                'date_rdv':          str(mission.date_rdv) if mission.date_rdv else None,
                'montant_devis':     mission.montant_devis,
                'reste_a_charge':    mission.reste_a_charge,
                'photos':            photos,
                'devis':             devis_data,
                'signature_avant':   bool(mission.signature_avant),
                'signature_apres':   bool(mission.signature_apres),
                'notes_artisan':     mission.notes_artisan or '',
                'messages_non_lus':  unread,
            }
        })

    # ─── DÉMARRER LES TRAVAUX ───────────────────────────────────────
    @http.route('/api/sinistre/v1/intervenant/mission/<int:mission_id>/demarrer',
                type='http', auth='user', methods=['POST'], csrf=False)
    def demarrer_mission(self, mission_id, **kwargs):
        intervenant = _get_intervenant()
        if not intervenant:
            return _json_error(403, "Accès non autorisé")
        mission = _check_mission(intervenant, mission_id)
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
        mission = _check_mission(intervenant, mission_id)
        if not mission:
            return _json_error(404, "Mission introuvable")
        try:
            mission.action_terminer()
            return _json_response({'success': True, 'state': mission.state})
        except Exception as e:
            return _json_error(400, str(e))

    # ─── SIGNATURE AVANT INTERVENTION ───────────────────────────────
    @http.route('/api/sinistre/v1/intervenant/mission/<int:mission_id>/signature-avant',
                type='http', auth='user', methods=['POST'], csrf=False)
    def signature_avant(self, mission_id, **kwargs):
        intervenant = _get_intervenant()
        if not intervenant:
            return _json_error(403, "Accès non autorisé")
        mission = _check_mission(intervenant, mission_id)
        if not mission:
            return _json_error(404, "Mission introuvable")
        try:
            body = json.loads(request.httprequest.data.decode('utf-8'))
        except Exception:
            return _json_error(400, "Body JSON invalide")
        sig = body.get('signature', '')
        if not sig:
            return _json_error(400, "Signature requise")
        try:
            mission.sudo().write({'signature_avant': sig})
            mission.message_post(body=_("✅ Signature avant intervention enregistrée par l'artisan."))
            return _json_response({'success': True})
        except Exception as e:
            return _json_error(500, str(e))

    # ─── SIGNATURE APRÈS INTERVENTION ───────────────────────────────
    @http.route('/api/sinistre/v1/intervenant/mission/<int:mission_id>/signature-apres',
                type='http', auth='user', methods=['POST'], csrf=False)
    def signature_apres(self, mission_id, **kwargs):
        intervenant = _get_intervenant()
        if not intervenant:
            return _json_error(403, "Accès non autorisé")
        mission = _check_mission(intervenant, mission_id)
        if not mission:
            return _json_error(404, "Mission introuvable")
        try:
            body = json.loads(request.httprequest.data.decode('utf-8'))
        except Exception:
            return _json_error(400, "Body JSON invalide")
        sig = body.get('signature', '')
        if not sig:
            return _json_error(400, "Signature requise")
        try:
            mission.sudo().write({'signature_apres': sig})
            mission.message_post(body=_("✅ Signature après intervention enregistrée — génération facture."))
            if hasattr(mission, 'action_generer_facture'):
                try:
                    mission.action_generer_facture()
                except Exception as fe:
                    _logger.warning(f"Facture auto échouée pour mission {mission.id}: {fe}")
            return _json_response({'success': True, 'facture': bool(mission.facture_client_id)})
        except Exception as e:
            return _json_error(500, str(e))

    # ─── CRÉER UN DEVIS ─────────────────────────────────────────────
    @http.route('/api/sinistre/v1/intervenant/mission/<int:mission_id>/devis',
                type='http', auth='user', methods=['POST'], csrf=False)
    def creer_devis(self, mission_id, **kwargs):
        intervenant = _get_intervenant()
        if not intervenant:
            return _json_error(403, "Accès non autorisé")
        mission = _check_mission(intervenant, mission_id)
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
            devis = request.env['sinistre.devis'].sudo().create({
                'mission_id':  mission.id,
                'note_client': body.get('note_client', ''),
                'tva':         body.get('tva', 20.0),
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

    # ─── MODIFIER UN DEVIS ──────────────────────────────────────────
    @http.route('/api/sinistre/v1/intervenant/devis/<int:devis_id>',
                type='http', auth='user', methods=['PUT'], csrf=False)
    def modifier_devis(self, devis_id, **kwargs):
        intervenant = _get_intervenant()
        if not intervenant:
            return _json_error(403, "Accès non autorisé")
        devis = request.env['sinistre.devis'].sudo().search([
            ('id', '=', devis_id),
            ('mission_id.intervenant_id', '=', intervenant.id),
        ], limit=1)
        if not devis:
            return _json_error(404, "Devis introuvable")
        try:
            body = json.loads(request.httprequest.data.decode('utf-8'))
        except Exception:
            return _json_error(400, "Body JSON invalide")
        is_amendment = body.get('is_amendment', False)
        lignes = body.get('ligne_ids', [])
        if not lignes:
            return _json_error(400, "Au moins une ligne est requise")
        try:
            devis.sudo().ligne_ids.unlink()
            devis.sudo().write({
                'note_client': body.get('note_client', devis.note_client),
                'ligne_ids': [(0, 0, {
                    'description':   l['description'],
                    'quantite':      float(l.get('quantite', 1)),
                    'prix_unitaire': float(l.get('prix_unitaire', 0)),
                    'unite':         l.get('unite', 'forfait'),
                }) for l in lignes],
            })
            if is_amendment:
                devis.sudo().write({'state': 'en_revision'})
                devis.mission_id.message_post(
                    body=_("⚠️ Devis modifié par l'artisan pendant l'intervention — re-signature client requise.")
                )
            return _json_response({
                'success': True,
                'devis_id': devis.id,
                'state': devis.state,
                'montant_total': devis.montant_total,
            })
        except Exception as e:
            return _json_error(500, str(e))

    # ─── ENVOYER LE DEVIS ───────────────────────────────────────────
    @http.route('/api/sinistre/v1/intervenant/devis/<int:devis_id>/envoyer',
                type='http', auth='user', methods=['POST'], csrf=False)
    def envoyer_devis(self, devis_id, **kwargs):
        intervenant = _get_intervenant()
        if not intervenant:
            return _json_error(403, "Accès non autorisé")
        devis = request.env['sinistre.devis'].sudo().search([
            ('id', '=', devis_id),
            ('mission_id.intervenant_id', '=', intervenant.id),
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
        devis = request.env['sinistre.devis'].sudo().search([
            ('id', '=', devis_id),
            ('mission_id.intervenant_id', '=', intervenant.id),
        ], limit=1)
        if not devis:
            return _json_error(404, "Devis introuvable")
        try:
            body = json.loads(request.httprequest.data.decode('utf-8'))
        except Exception:
            body = {}
        sig         = body.get('signature', '')
        is_modified = body.get('is_modified', False)
        sig_field   = 'signature_client_modif' if is_modified else 'signature_client'
        try:
            devis.sudo().write({sig_field: sig or False})
            devis.action_accepter()
            if is_modified:
                devis.mission_id.message_post(
                    body=_("✅ Devis modifié re-signé par le client — travaux peuvent reprendre.")
                )
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
        devis = request.env['sinistre.devis'].sudo().search([
            ('id', '=', devis_id),
            ('mission_id.intervenant_id', '=', intervenant.id),
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
        mission = _check_mission(intervenant, mission_id)
        if not mission:
            return _json_error(404, "Mission introuvable")
        try:
            body = json.loads(request.httprequest.data.decode('utf-8'))
        except Exception:
            return _json_error(400, "Body JSON invalide")
        image_b64  = body.get('image', '')
        type_photo = body.get('type_photo', 'avant')
        if not image_b64:
            return _json_error(400, "Image base64 requise")
        if type_photo not in ('avant', 'pendant', 'apres'):
            type_photo = 'avant'
        try:
            photo = request.env['sinistre.photo'].sudo().create({
                'mission_id':     mission.id,
                'type_photo':     type_photo,
                'image':          image_b64,
                'description':    body.get('description', ''),
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

    # ─── NOTES ARTISAN ──────────────────────────────────────────────
    @http.route('/api/sinistre/v1/intervenant/mission/<int:mission_id>/notes',
                type='http', auth='user', methods=['POST'], csrf=False)
    def save_notes(self, mission_id, **kwargs):
        intervenant = _get_intervenant()
        if not intervenant:
            return _json_error(403, "Accès non autorisé")
        mission = _check_mission(intervenant, mission_id)
        if not mission:
            return _json_error(404, "Mission introuvable")
        try:
            body = json.loads(request.httprequest.data.decode('utf-8'))
        except Exception:
            return _json_error(400, "Body JSON invalide")
        try:
            mission.sudo().write({'notes_artisan': body.get('notes', '')})
            return _json_response({'success': True})
        except Exception as e:
            return _json_error(500, str(e))

    # ─── MESSAGERIE : GET ────────────────────────────────────────────
    @http.route('/api/sinistre/v1/intervenant/mission/<int:mission_id>/messages',
                type='http', auth='user', methods=['GET'], csrf=False)
    def get_messages(self, mission_id, **kwargs):
        intervenant = _get_intervenant()
        if not intervenant:
            return _json_error(403, "Accès non autorisé")
        mission = _check_mission(intervenant, mission_id)
        if not mission:
            return _json_error(404, "Mission introuvable")
        msgs = request.env['sinistre.message'].sudo().search([
            ('mission_id', '=', mission.id)
        ], order='date_envoi asc')
        return _json_response({
            'success': True,
            'messages': [{
                'id':          m.id,
                'auteur_type': m.auteur_type,
                'auteur_nom':  m.auteur_nom or '',
                'contenu':     m.contenu,
                'date_envoi':  str(m.date_envoi),
                'lu_artisan':  m.lu_artisan,
            } for m in msgs],
        })

    # ─── MESSAGERIE : POST ───────────────────────────────────────────
    @http.route('/api/sinistre/v1/intervenant/mission/<int:mission_id>/messages',
                type='http', auth='user', methods=['POST'], csrf=False)
    def send_message(self, mission_id, **kwargs):
        intervenant = _get_intervenant()
        if not intervenant:
            return _json_error(403, "Accès non autorisé")
        mission = _check_mission(intervenant, mission_id)
        if not mission:
            return _json_error(404, "Mission introuvable")
        try:
            body    = json.loads(request.httprequest.data.decode('utf-8'))
            contenu = (body.get('contenu') or '').strip()
        except Exception:
            return _json_error(400, "Body JSON invalide")
        if not contenu:
            return _json_error(400, "Contenu du message requis")
        try:
            msg = request.env['sinistre.message'].sudo().create({
                'mission_id':  mission.id,
                'auteur_type': 'artisan',
                'auteur_nom':  intervenant.name or request.env.user.name,
                'contenu':     contenu,
                'lu_artisan':  True,
            })
            return _json_response({
                'success': True,
                'message': {
                    'id':          msg.id,
                    'auteur_type': msg.auteur_type,
                    'auteur_nom':  msg.auteur_nom,
                    'contenu':     msg.contenu,
                    'date_envoi':  str(msg.date_envoi),
                },
            }, status=201)
        except Exception as e:
            return _json_error(500, str(e))

    # ─── MESSAGERIE : MARQUER LUS ────────────────────────────────────
    @http.route('/api/sinistre/v1/intervenant/mission/<int:mission_id>/messages/lus',
                type='http', auth='user', methods=['POST'], csrf=False)
    def marquer_lus(self, mission_id, **kwargs):
        intervenant = _get_intervenant()
        if not intervenant:
            return _json_error(403, "Accès non autorisé")
        mission = _check_mission(intervenant, mission_id)
        if not mission:
            return _json_error(404, "Mission introuvable")
        request.env['sinistre.message'].sudo().search([
            ('mission_id', '=', mission.id),
            ('lu_artisan', '=', False),
            ('auteur_type', '!=', 'artisan'),
        ]).write({'lu_artisan': True})
        return _json_response({'success': True})


    # ─── MISSIONS PROPOSÉES : liste ─────────────────────────────────
    @http.route('/api/sinistre/v1/intervenant/missions/proposees',
                type='http', auth='user', methods=['GET'], csrf=False)
    def get_missions_proposees(self, **kwargs):
        intervenant = _get_intervenant()
        if not intervenant:
            return _json_error(403, "Accès non autorisé")
        # Missions en état "nouveau" non encore assignées à un intervenant
        # OU missions assignées à cet intervenant en attente de confirmation
        missions = request.env['sinistre.mission'].sudo().search([
            ('state', '=', 'nouveau'),
            ('intervenant_id', '=', False),
        ], order='urgence desc, date_reception asc', limit=20)
        result = []
        for m in missions:
            result.append({
                'id':                m.id,
                'reference':         m.reference,
                'state':             m.state,
                'type_intervention': m.type_intervention,
                'urgence':           m.urgence,
                'description':       m.description_sinistre or '',
                'adresse':           m.adresse_intervention or '',
                'date_rdv':          str(m.date_rdv) if m.date_rdv else None,
                'montant_garanti':   m.montant_garanti or 0,
                'montant_devis':     m.montant_devis or 0,
                'montant_estime':    m.montant_estime or 0,
                'montant_estime_max':m.montant_estime_max or 0,
                'source':            m.source,
            })
        return _json_response({'success': True, 'missions': result})

    # ─── ACCEPTER UNE MISSION PROPOSÉE ──────────────────────────────
    @http.route('/api/sinistre/v1/intervenant/mission/<int:mission_id>/accepter',
                type='http', auth='user', methods=['POST'], csrf=False)
    def accepter_mission(self, mission_id, **kwargs):
        intervenant = _get_intervenant()
        if not intervenant:
            return _json_error(403, "Accès non autorisé")
        mission = request.env['sinistre.mission'].sudo().search([
            ('id', '=', mission_id),
            ('state', '=', 'nouveau'),
        ], limit=1)
        if not mission:
            return _json_error(404, "Mission introuvable ou déjà assignée")
        try:
            mission.sudo().write({
                'intervenant_id': intervenant.id,
                'state':          'assigne',
            })
            mission.message_post(
                body=_(f"✅ Mission acceptée par {intervenant.name}.")
            )
            return _json_response({'success': True, 'state': mission.state, 'mission_id': mission.id})
        except Exception as e:
            return _json_error(500, str(e))

    # ─── REFUSER UNE MISSION PROPOSÉE ───────────────────────────────
    @http.route('/api/sinistre/v1/intervenant/mission/<int:mission_id>/refuser-proposition',
                type='http', auth='user', methods=['POST'], csrf=False)
    def refuser_proposition(self, mission_id, **kwargs):
        intervenant = _get_intervenant()
        if not intervenant:
            return _json_error(403, "Accès non autorisé")
        mission = request.env['sinistre.mission'].sudo().search([
            ('id', '=', mission_id),
            ('state', '=', 'nouveau'),
        ], limit=1)
        if not mission:
            return _json_error(404, "Mission introuvable")
        try:
            mission.message_post(
                body=_(f"❌ Mission refusée par {intervenant.name}.")
            )
            return _json_response({'success': True})
        except Exception as e:
            return _json_error(500, str(e))

    # ─── FCM TOKEN ───────────────────────────────────────────────────
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
        intervenant.sudo().write({'fcm_token': token})
        return _json_response({'success': True, 'message': 'Token FCM enregistré'})
