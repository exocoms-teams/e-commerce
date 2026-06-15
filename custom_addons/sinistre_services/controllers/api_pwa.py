# -*- coding: utf-8 -*-
"""
api_pwa.py — Controller unique PWA / API Sinistre
Toutes les routes /api/sinistre/v1/ gérées ici.
"""
import json
import logging

from odoo import http, _
from odoo.http import request, Response

_logger = logging.getLogger(__name__)

PREFIX = '/api/sinistre/v1'


# ══════════════════════════════════════════════════════════════════════
#  Helpers partagés
# ══════════════════════════════════════════════════════════════════════

def _ok(data, status=200):
    return Response(
        json.dumps(data, default=str, ensure_ascii=False),
        status=status,
        content_type='application/json; charset=utf-8',
    )

def _err(status, message):
    return _ok({'success': False, 'error': message}, status=status)

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
    """Retourne la mission si elle appartient à cet intervenant, None sinon."""
    return request.env['sinistre.mission'].sudo().search([
        ('id', '=', mission_id),
        ('intervenant_id', '=', intervenant.id),
    ], limit=1)

def _fmt_mission(m):
    return {
        'id':                   m.id,
        'reference':            m.reference,
        'state':                m.state,
        'source':               m.source if hasattr(m, 'source') else '',
        'type_intervention':    m.type_intervention,
        'urgence':              m.urgence,
        'client':               m.client_id.name if m.client_id else '',
        'tel_sur_place':        m.tel_sur_place or '',
        'contact_sur_place':    m.contact_sur_place or '',
        'adresse':              m.adresse_intervention or '',
        'adresse_intervention': m.adresse_intervention or '',
        'date_rdv':             str(m.date_rdv) if m.date_rdv else None,
        'description':          m.description_sinistre or '',
        'description_sinistre': m.description_sinistre or '',
        'montant_devis':        m.montant_devis or 0,
        'montant_garanti':      m.montant_garanti or 0,
        'montant_estime':       m.montant_estime or 0,
        'montant_estime_max':   m.montant_estime_max or 0,
        'reste_a_charge':       m.reste_a_charge or 0,
        'signature_avant':      bool(m.signature_avant),
        'signature_apres':      bool(m.signature_apres),
        'notes_artisan':        m.notes_artisan or '',
    }


# ══════════════════════════════════════════════════════════════════════
#  Controller principal
# ══════════════════════════════════════════════════════════════════════

class SinistrePWAController(http.Controller):

    # ── PING ─────────────────────────────────────────────────────────
    @http.route(f'{PREFIX}/ping', type='http', auth='public',
                methods=['GET'], csrf=False)
    def ping(self, **kw):
        return _ok({'success': True, 'status': 'ok'})

    # ── ME ───────────────────────────────────────────────────────────
    @http.route(f'{PREFIX}/me', type='http', auth='user',
                methods=['GET'], csrf=False)
    def me(self, **kw):
        user = request.env.user
        iv   = _get_intervenant()

        terminees = request.env['sinistre.mission'].sudo().search([
            ('intervenant_id', '=', iv.id),
            ('state', 'in', ('termine', 'clos', 'facture')),
        ])
        nb_terminees = len(terminees)
        ca_total = sum(m.montant_devis or 0 for m in terminees)

        from datetime import datetime
        now = datetime.now()
        ca_mois = sum(
            m.montant_devis or 0 for m in terminees
            if m.date_cloture
            and m.date_cloture.month == now.month
            and m.date_cloture.year == now.year
        )

        note = round(ca_total / nb_terminees / 100, 1) if nb_terminees else 0
        note = min(note, 5.0) if note else 0

        certifications = []
        try:
            for cert in (iv.certification_ids or []):
                if cert.date_validite:
                    date_label = f"Valide jusqu'en {cert.date_validite.strftime('%Y')}"
                else:
                    date_label = 'À jour'
                certifications.append({'name': cert.name, 'date': date_label})
        except Exception:
            certifications = []

        specialites       = []
        specialites_types = []
        for s in (iv.specialites or []):
            specialites.append(s.name)
            if hasattr(s, 'type_intervention') and s.type_intervention:
                specialites_types.append(s.type_intervention)

        membre_depuis = ''
        try:
            cd = user.create_date
            if cd:
                mois_fr = {
                    1:'Janvier', 2:'Février', 3:'Mars', 4:'Avril',
                    5:'Mai', 6:'Juin', 7:'Juillet', 8:'Août',
                    9:'Septembre', 10:'Octobre', 11:'Novembre', 12:'Décembre',
                }
                membre_depuis = f"{mois_fr.get(cd.month, '')} {cd.year}"
        except Exception:
            membre_depuis = ''

        partner    = user.partner_id
        phone      = partner.phone or partner.mobile or ''
        entreprise = iv.name or (partner.parent_id.name if partner.parent_id else '') or user.name

        return _ok({'success': True, 'user': {
            'uid':               user.id,
            'name':              user.name,
            'email':             user.login,
            'phone':             phone,
            'company_name':      entreprise,
            'zone':              iv.zone_intervention or '',
            'note_moyenne':      note,
            'interventions':     nb_terminees,
            'ca_total':          ca_total,
            'ca_mois':           ca_mois,
            'specialites':       specialites,
            'specialites_types': specialites_types,
            'membre_depuis':     membre_depuis,
            'intervenant_id':    iv.id,
            'create_date':       str(user.create_date) if user.create_date else '',
            'certifications':    certifications,
        }})

    # ── MES MISSIONS ─────────────────────────────────────────────────
    @http.route(f'{PREFIX}/intervenant/missions', type='http',
                auth='user', methods=['GET'], csrf=False)
    def mes_missions(self, **kw):
        iv = _get_intervenant()
        if not iv:
            return _err(403, "Accès non autorisé")
        missions = request.env['sinistre.mission'].sudo().search([
            ('intervenant_id', '=', iv.id),
            ('state', 'not in', ('clos', 'annule')),
        ], order='urgence desc, date_rdv asc')
        return _ok({'success': True, 'missions': [_fmt_mission(m) for m in missions],
                    'total': len(missions)})

    # ── DÉTAIL MISSION ───────────────────────────────────────────────
    @http.route(f'{PREFIX}/mission/<string:reference>',
                type='http', auth='user', methods=['GET'], csrf=False)
    def get_mission_detail(self, reference, **kwargs):
        intervenant = _get_intervenant()
        if not intervenant:
            return _err(403, "Accès non autorisé")

        domain = [('intervenant_id', '=', intervenant.id)]
        if reference.isdigit():
            domain.append(('id', '=', int(reference)))
        else:
            domain.append(('reference', '=', reference))

        mission = request.env['sinistre.mission'].sudo().search(domain, limit=1)
        if not mission:
            return _err(404, "Mission introuvable")

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

        data = _fmt_mission(mission)
        data.update({'photos': photos, 'devis': devis_data, 'messages_non_lus': unread})
        return _ok({'success': True, 'mission': data})

    # ── DÉMARRER ─────────────────────────────────────────────────────
    @http.route(f'{PREFIX}/intervenant/mission/<int:mission_id>/demarrer',
                type='http', auth='user', methods=['POST'], csrf=False)
    def demarrer_mission(self, mission_id, **kwargs):
        intervenant = _get_intervenant()
        if not intervenant:
            return _err(403, "Accès non autorisé")
        mission = _check_mission(intervenant, mission_id)
        if not mission:
            return _err(404, "Mission introuvable")
        try:
            mission.action_demarrer()
            return _ok({'success': True, 'state': mission.state})
        except Exception as e:
            return _err(400, str(e))

    # ── TERMINER ─────────────────────────────────────────────────────
    @http.route(f'{PREFIX}/intervenant/mission/<int:mission_id>/terminer',
                type='http', auth='user', methods=['POST'], csrf=False)
    def terminer_mission(self, mission_id, **kwargs):
        intervenant = _get_intervenant()
        if not intervenant:
            return _err(403, "Accès non autorisé")
        mission = _check_mission(intervenant, mission_id)
        if not mission:
            return _err(404, "Mission introuvable")
        try:
            mission.action_terminer()
            return _ok({'success': True, 'state': mission.state})
        except Exception as e:
            return _err(400, str(e))

    # ── SIGNATURE AVANT ──────────────────────────────────────────────
    @http.route(f'{PREFIX}/intervenant/mission/<int:mission_id>/signature-avant',
                type='http', auth='user', methods=['POST'], csrf=False)
    def signature_avant(self, mission_id, **kwargs):
        intervenant = _get_intervenant()
        if not intervenant:
            return _err(403, "Accès non autorisé")
        mission = _check_mission(intervenant, mission_id)
        if not mission:
            return _err(404, "Mission introuvable")
        try:
            body = json.loads(request.httprequest.data.decode('utf-8'))
        except Exception:
            return _err(400, "Body JSON invalide")
        sig = body.get('signature', '')
        if not sig:
            return _err(400, "Signature requise")
        try:
            mission.sudo().write({'signature_avant': sig})
            mission.message_post(body=_("✅ Signature avant intervention enregistrée par l'artisan."))
            return _ok({'success': True})
        except Exception as e:
            return _err(500, str(e))

    # ── SIGNATURE APRÈS ──────────────────────────────────────────────
    @http.route(f'{PREFIX}/intervenant/mission/<int:mission_id>/signature-apres',
                type='http', auth='user', methods=['POST'], csrf=False)
    def signature_apres(self, mission_id, **kwargs):
        intervenant = _get_intervenant()
        if not intervenant:
            return _err(403, "Accès non autorisé")
        mission = _check_mission(intervenant, mission_id)
        if not mission:
            return _err(404, "Mission introuvable")
        try:
            body = json.loads(request.httprequest.data.decode('utf-8'))
        except Exception:
            return _err(400, "Body JSON invalide")
        sig = body.get('signature', '')
        if not sig:
            return _err(400, "Signature requise")
        try:
            mission.sudo().write({'signature_apres': sig})
            mission.message_post(body=_("✅ Signature après intervention enregistrée — génération facture."))
            if hasattr(mission, 'action_generer_facture'):
                try:
                    mission.action_generer_facture()
                except Exception as fe:
                    _logger.warning(f"Facture auto échouée pour mission {mission.id}: {fe}")
            return _ok({'success': True, 'facture': bool(mission.facture_client_id)})
        except Exception as e:
            return _err(500, str(e))

    # ── UPLOAD PHOTO ─────────────────────────────────────────────────
    @http.route(f'{PREFIX}/intervenant/mission/<int:mission_id>/photo',
                type='http', auth='user', methods=['POST'], csrf=False)
    def upload_photo(self, mission_id, **kwargs):
        intervenant = _get_intervenant()
        if not intervenant:
            return _err(403, "Accès non autorisé")
        mission = _check_mission(intervenant, mission_id)
        if not mission:
            return _err(404, "Mission introuvable")
        try:
            body = json.loads(request.httprequest.data.decode('utf-8'))
        except Exception:
            return _err(400, "Body JSON invalide")
        image_b64  = body.get('image', '')
        type_photo = body.get('type_photo', 'avant')
        if not image_b64:
            return _err(400, "Image base64 requise")
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
            return _ok({
                'success':   True,
                'photo_id':  photo.id,
                'type_photo': type_photo,
                'url': f'/web/image/sinistre.photo/{photo.id}/image',
            }, status=201)
        except Exception as e:
            _logger.error(f"[sinistre] upload_photo: {e}", exc_info=True)
            return _err(500, str(e))

    # ── NOTES ARTISAN ────────────────────────────────────────────────
    @http.route(f'{PREFIX}/intervenant/mission/<int:mission_id>/notes',
                type='http', auth='user', methods=['POST'], csrf=False)
    def save_notes(self, mission_id, **kwargs):
        intervenant = _get_intervenant()
        if not intervenant:
            return _err(403, "Accès non autorisé")
        mission = _check_mission(intervenant, mission_id)
        if not mission:
            return _err(404, "Mission introuvable")
        try:
            body = json.loads(request.httprequest.data.decode('utf-8'))
        except Exception:
            return _err(400, "Body JSON invalide")
        try:
            mission.sudo().write({'notes_artisan': body.get('notes', '')})
            return _ok({'success': True})
        except Exception as e:
            return _err(500, str(e))

    # ── CRÉER DEVIS ──────────────────────────────────────────────────
    @http.route(f'{PREFIX}/intervenant/mission/<int:mission_id>/devis',
                type='http', auth='user', methods=['POST'], csrf=False)
    def creer_devis(self, mission_id, **kwargs):
        intervenant = _get_intervenant()
        if not intervenant:
            return _err(403, "Accès non autorisé")
        mission = _check_mission(intervenant, mission_id)
        if not mission:
            return _err(404, "Mission introuvable")
        try:
            body = json.loads(request.httprequest.data.decode('utf-8'))
        except Exception:
            return _err(400, "Body JSON invalide")
        lignes = body.get('ligne_ids', [])
        if not lignes:
            return _err(400, "Au moins une ligne est requise")
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
            return _ok({
                'success':       True,
                'devis_id':      devis.id,
                'name':          devis.name,
                'montant_ht':    devis.montant_ht,
                'montant_total': devis.montant_total,
            }, status=201)
        except Exception as e:
            _logger.error(f"[sinistre] creer_devis: {e}", exc_info=True)
            return _err(500, str(e))

    # ── MODIFIER DEVIS ───────────────────────────────────────────────
    @http.route(f'{PREFIX}/intervenant/devis/<int:devis_id>',
                type='http', auth='user', methods=['PUT'], csrf=False)
    def modifier_devis(self, devis_id, **kwargs):
        intervenant = _get_intervenant()
        if not intervenant:
            return _err(403, "Accès non autorisé")
        devis = request.env['sinistre.devis'].sudo().search([
            ('id', '=', devis_id),
            ('mission_id.intervenant_id', '=', intervenant.id),
        ], limit=1)
        if not devis:
            return _err(404, "Devis introuvable")
        try:
            body = json.loads(request.httprequest.data.decode('utf-8'))
        except Exception:
            return _err(400, "Body JSON invalide")
        lignes = body.get('ligne_ids', [])
        if not lignes:
            return _err(400, "Au moins une ligne est requise")
        is_amendment = body.get('is_amendment', False)
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
            return _ok({
                'success':       True,
                'devis_id':      devis.id,
                'state':         devis.state,
                'montant_total': devis.montant_total,
            })
        except Exception as e:
            return _err(500, str(e))

    # ── ENVOYER DEVIS ────────────────────────────────────────────────
    @http.route(f'{PREFIX}/intervenant/devis/<int:devis_id>/envoyer',
                type='http', auth='user', methods=['POST'], csrf=False)
    def envoyer_devis(self, devis_id, **kwargs):
        intervenant = _get_intervenant()
        if not intervenant:
            return _err(403, "Accès non autorisé")
        devis = request.env['sinistre.devis'].sudo().search([
            ('id', '=', devis_id),
            ('mission_id.intervenant_id', '=', intervenant.id),
        ], limit=1)
        if not devis:
            return _err(404, "Devis introuvable")
        try:
            devis.action_envoyer()
            return _ok({'success': True, 'state': devis.state})
        except Exception as e:
            return _err(400, str(e))

    # ── ACCEPTER DEVIS ───────────────────────────────────────────────
    @http.route(f'{PREFIX}/intervenant/devis/<int:devis_id>/accepter',
                type='http', auth='user', methods=['POST'], csrf=False)
    def accepter_devis(self, devis_id, **kwargs):
        intervenant = _get_intervenant()
        if not intervenant:
            return _err(403, "Accès non autorisé")
        devis = request.env['sinistre.devis'].sudo().search([
            ('id', '=', devis_id),
            ('mission_id.intervenant_id', '=', intervenant.id),
        ], limit=1)
        if not devis:
            return _err(404, "Devis introuvable")
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
            return _ok({'success': True, 'state': devis.state})
        except Exception as e:
            return _err(400, str(e))

    # ── REFUSER DEVIS ────────────────────────────────────────────────
    @http.route(f'{PREFIX}/intervenant/devis/<int:devis_id>/refuser',
                type='http', auth='user', methods=['POST'], csrf=False)
    def refuser_devis(self, devis_id, **kwargs):
        intervenant = _get_intervenant()
        if not intervenant:
            return _err(403, "Accès non autorisé")
        devis = request.env['sinistre.devis'].sudo().search([
            ('id', '=', devis_id),
            ('mission_id.intervenant_id', '=', intervenant.id),
        ], limit=1)
        if not devis:
            return _err(404, "Devis introuvable")
        try:
            devis.action_refuser()
            return _ok({'success': True, 'state': devis.state})
        except Exception as e:
            return _err(400, str(e))

    # ── MESSAGERIE : GET ─────────────────────────────────────────────
    @http.route(f'{PREFIX}/intervenant/mission/<int:mission_id>/messages',
                type='http', auth='user', methods=['GET'], csrf=False)
    def get_messages(self, mission_id, **kwargs):
        intervenant = _get_intervenant()
        if not intervenant:
            return _err(403, "Accès non autorisé")
        mission = _check_mission(intervenant, mission_id)
        if not mission:
            return _err(404, "Mission introuvable")
        msgs = request.env['sinistre.message'].sudo().search([
            ('mission_id', '=', mission.id)
        ], order='date_envoi asc')
        return _ok({
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

    # ── MESSAGERIE : POST ────────────────────────────────────────────
    @http.route(f'{PREFIX}/intervenant/mission/<int:mission_id>/messages',
                type='http', auth='user', methods=['POST'], csrf=False)
    def send_message(self, mission_id, **kwargs):
        intervenant = _get_intervenant()
        if not intervenant:
            return _err(403, "Accès non autorisé")
        mission = _check_mission(intervenant, mission_id)
        if not mission:
            return _err(404, "Mission introuvable")
        try:
            body    = json.loads(request.httprequest.data.decode('utf-8'))
            contenu = (body.get('contenu') or '').strip()
        except Exception:
            return _err(400, "Body JSON invalide")
        if not contenu:
            return _err(400, "Contenu du message requis")
        try:
            msg = request.env['sinistre.message'].sudo().create({
                'mission_id':  mission.id,
                'auteur_type': 'artisan',
                'auteur_nom':  intervenant.name or request.env.user.name,
                'contenu':     contenu,
                'lu_artisan':  True,
            })
            return _ok({
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
            return _err(500, str(e))

    # ── MESSAGERIE : MARQUER LUS ─────────────────────────────────────
    @http.route(f'{PREFIX}/intervenant/mission/<int:mission_id>/messages/lus',
                type='http', auth='user', methods=['POST'], csrf=False)
    def marquer_lus(self, mission_id, **kwargs):
        intervenant = _get_intervenant()
        if not intervenant:
            return _err(403, "Accès non autorisé")
        mission = _check_mission(intervenant, mission_id)
        if not mission:
            return _err(404, "Mission introuvable")
        request.env['sinistre.message'].sudo().search([
            ('mission_id', '=', mission.id),
            ('lu_artisan', '=', False),
            ('auteur_type', '!=', 'artisan'),
        ]).write({'lu_artisan': True})
        return _ok({'success': True})

    # ── MISSIONS PROPOSÉES ───────────────────────────────────────────
    @http.route(f'{PREFIX}/intervenant/missions/proposees',
                type='http', auth='user', methods=['GET'], csrf=False)
    def get_missions_proposees(self, **kwargs):
        intervenant = _get_intervenant()
        if not intervenant:
            return _err(403, "Accès non autorisé")
        missions = request.env['sinistre.mission'].sudo().search([
            ('state', '=', 'nouveau'),
            ('intervenant_id', '=', False),
        ], order='urgence desc, date_reception asc', limit=20)
        result = [{
            'id':                 m.id,
            'reference':          m.reference,
            'state':              m.state,
            'type_intervention':  m.type_intervention,
            'urgence':            m.urgence,
            'description':        m.description_sinistre or '',
            'adresse':            m.adresse_intervention or '',
            'date_rdv':           str(m.date_rdv) if m.date_rdv else None,
            'montant_garanti':    m.montant_garanti or 0,
            'montant_devis':      m.montant_devis or 0,
            'montant_estime':     m.montant_estime or 0,
            'montant_estime_max': m.montant_estime_max or 0,
            'source':             m.source,
        } for m in missions]
        return _ok({'success': True, 'missions': result})

    # ── ACCEPTER MISSION PROPOSÉE ────────────────────────────────────
    @http.route(f'{PREFIX}/intervenant/mission/<int:mission_id>/accepter',
                type='http', auth='user', methods=['POST'], csrf=False)
    def accepter_mission(self, mission_id, **kwargs):
        intervenant = _get_intervenant()
        if not intervenant:
            return _err(403, "Accès non autorisé")
        mission = request.env['sinistre.mission'].sudo().search([
            ('id', '=', mission_id),
            ('state', '=', 'nouveau'),
        ], limit=1)
        if not mission:
            return _err(404, "Mission introuvable ou déjà assignée")
        try:
            mission.sudo().write({'intervenant_id': intervenant.id, 'state': 'assigne'})
            mission.message_post(body=_(f"✅ Mission acceptée par {intervenant.name}."))
            return _ok({'success': True, 'state': mission.state, 'mission_id': mission.id})
        except Exception as e:
            return _err(500, str(e))

    # ── REFUSER MISSION PROPOSÉE ─────────────────────────────────────
    @http.route(f'{PREFIX}/intervenant/mission/<int:mission_id>/refuser-proposition',
                type='http', auth='user', methods=['POST'], csrf=False)
    def refuser_proposition(self, mission_id, **kwargs):
        intervenant = _get_intervenant()
        if not intervenant:
            return _err(403, "Accès non autorisé")
        mission = request.env['sinistre.mission'].sudo().search([
            ('id', '=', mission_id),
            ('state', '=', 'nouveau'),
        ], limit=1)
        if not mission:
            return _err(404, "Mission introuvable")
        try:
            mission.message_post(body=_(f"❌ Mission refusée par {intervenant.name}."))
            return _ok({'success': True})
        except Exception as e:
            return _err(500, str(e))

    # ── FCM TOKEN ────────────────────────────────────────────────────
    @http.route(f'{PREFIX}/intervenant/fcm-token',
                type='http', auth='user', methods=['POST'], csrf=False)
    def save_fcm_token(self, **kwargs):
        intervenant = _get_intervenant()
        if not intervenant:
            return _err(403, "Accès non autorisé")
        try:
            body  = json.loads(request.httprequest.data.decode('utf-8'))
            token = body.get('token', '').strip()
        except Exception:
            return _err(400, "Body JSON invalide")
        if not token:
            return _err(400, "Token FCM requis")
        intervenant.sudo().write({'fcm_token': token})
        return _ok({'success': True, 'message': 'Token FCM enregistré'})

    # ── PLANNING : GET ───────────────────────────────────────────────
    @http.route(f'{PREFIX}/intervenant/planning',
                type='http', auth='user', methods=['GET'], csrf=False)
    def planning_get(self, **kwargs):
        intervenant = _get_intervenant()
        if not intervenant:
            return _err(403, "Accès non autorisé")
        try:
            slots = intervenant.get_planning_slots()
            from odoo.fields import Date
            today    = Date.today()
            absences = intervenant.absence_ids.filtered(lambda a: a.date_fin and a.date_fin >= today)
            return _ok({
                'success':  True,
                'slots':    slots,
                'absences': [a._fmt() for a in absences.sorted('date_debut')],
            })
        except Exception as e:
            _logger.error(f"[sinistre] planning_get: {e}", exc_info=True)
            return _err(500, str(e))

    # ── PLANNING : SAVE ──────────────────────────────────────────────
    @http.route(f'{PREFIX}/intervenant/planning',
                type='http', auth='user', methods=['POST'], csrf=False)
    def planning_save(self, **kwargs):
        intervenant = _get_intervenant()
        if not intervenant:
            return _err(403, "Accès non autorisé")
        try:
            data  = json.loads((request.httprequest.data or b'{}').decode('utf-8'))
            slots = data.get('slots', {})
            intervenant.set_planning_slots(slots)
            return _ok({'success': True})
        except Exception as e:
            _logger.error(f"[sinistre] planning_save: {e}", exc_info=True)
            return _err(500, str(e))

    # ── ABSENCES : AJOUTER ───────────────────────────────────────────
    @http.route(f'{PREFIX}/intervenant/absences',
                type='http', auth='user', methods=['POST'], csrf=False)
    def absence_add(self, **kwargs):
        intervenant = _get_intervenant()
        if not intervenant:
            return _err(403, "Accès non autorisé")
        try:
            data       = json.loads((request.httprequest.data or b'{}').decode('utf-8'))
            date_debut = data.get('date_debut')
            date_fin   = data.get('date_fin')
            motif      = data.get('motif', '')
            if not date_debut or not date_fin:
                return _err(400, "date_debut et date_fin sont requis")
            request.env['sinistre.intervenant.absence'].sudo().create({
                'intervenant_id': intervenant.id,
                'date_debut':     date_debut,
                'date_fin':       date_fin,
                'motif':          motif,
            })
            from odoo.fields import Date
            today    = Date.today()
            absences = intervenant.absence_ids.filtered(lambda a: a.date_fin and a.date_fin >= today)
            return _ok({'success': True,
                        'absences': [a._fmt() for a in absences.sorted('date_debut')]})
        except Exception as e:
            _logger.error(f"[sinistre] absence_add: {e}", exc_info=True)
            return _err(500, str(e))

    # ── ABSENCES : SUPPRIMER ─────────────────────────────────────────
    @http.route(f'{PREFIX}/intervenant/absences/delete',
                type='http', auth='user', methods=['POST'], csrf=False)
    def absence_delete(self, **kwargs):
        intervenant = _get_intervenant()
        if not intervenant:
            return _err(403, "Accès non autorisé")
        try:
            data       = json.loads((request.httprequest.data or b'{}').decode('utf-8'))
            absence_id = int(data.get('id', 0))
            absence    = request.env['sinistre.intervenant.absence'].sudo().browse(absence_id)
            if not absence.exists() or absence.intervenant_id.id != intervenant.id:
                return _err(404, "Absence introuvable ou accès interdit")
            absence.unlink()
            from odoo.fields import Date
            today    = Date.today()
            absences = intervenant.absence_ids.filtered(lambda a: a.date_fin and a.date_fin >= today)
            return _ok({'success': True,
                        'absences': [a._fmt() for a in absences.sorted('date_debut')]})
        except Exception as e:
            _logger.error(f"[sinistre] absence_delete: {e}", exc_info=True)
            return _err(500, str(e))

    # ── COORDONNÉES BANCAIRES : GET ──────────────────────────────────
    @http.route(f'{PREFIX}/intervenant/bancaire',
                type='http', auth='user', methods=['GET'], csrf=False)
    def bancaire_get(self, **kw):
        intervenant = _get_intervenant()
        if not intervenant:
            return _err(403, "Accès non autorisé")
        try:
            return _ok({'success': True, 'bancaire': {
                'iban':             intervenant.iban or '',
                'bic':              intervenant.bic  or '',
                'titulaire_compte': intervenant.titulaire_compte or '',
                'banque':           intervenant.banque or '',
            }})
        except Exception as e:
            return _err(500, str(e))

    # ── COORDONNÉES BANCAIRES : SAVE ─────────────────────────────────
    @http.route(f'{PREFIX}/intervenant/bancaire',
                type='http', auth='user', methods=['POST'], csrf=False)
    def bancaire_save(self, **kw):
        intervenant = _get_intervenant()
        if not intervenant:
            return _err(403, "Accès non autorisé")
        try:
            data = json.loads((request.httprequest.data or b'{}').decode('utf-8'))
            intervenant.sudo().write({
                'iban':             data.get('iban',      '').strip().upper(),
                'bic':              data.get('bic',       '').strip().upper(),
                'titulaire_compte': data.get('titulaire', '').strip(),
                'banque':           data.get('banque',    '').strip(),
            })
            return _ok({'success': True})
        except Exception as e:
            _logger.error(f"[sinistre] bancaire_save: {e}", exc_info=True)
            return _err(500, str(e))

    # ── DEMANDE PUBLIQUE ─────────────────────────────────────────────
    @http.route(f'{PREFIX}/mission', type='http', auth='public',
                methods=['POST'], csrf=False)
    def create_mission_public(self, **kw):
        try:
            data    = json.loads((request.httprequest.data or b'{}').decode('utf-8'))
            email   = data.get('email', '')
            partner = request.env['res.partner'].sudo().search(
                [('email', '=', email)], limit=1
            ) if email else None
            if not partner:
                partner = request.env['res.partner'].sudo().create({
                    'name':  data.get('nom', data.get('name', 'Client')),
                    'email': email,
                    'phone': data.get('tel', ''),
                })
            m = request.env['sinistre.mission'].sudo().create({
                'source':               data.get('source', 'particulier'),
                'client_id':            partner.id,
                'type_intervention':    data.get('type_intervention', 'autre'),
                'urgence':              data.get('urgence', 'normale'),
                'description_sinistre': data.get('description', 'Demande'),
                'adresse_intervention': data.get('adresse', ''),
                'tel_sur_place':        data.get('tel', ''),
            })
            return _ok({'success': True, 'reference': m.reference, 'id': m.id})
        except Exception as e:
            _logger.error(f"[sinistre] create_mission_public: {e}")
            return _err(500, str(e))
