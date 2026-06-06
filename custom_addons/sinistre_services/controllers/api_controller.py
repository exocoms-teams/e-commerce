# -*- coding: utf-8 -*-
import json
import base64
import logging
from odoo import http
from odoo.http import request, Response

_logger = logging.getLogger(__name__)


def _ok(data, status=200):
    return Response(
        json.dumps(data, default=str, ensure_ascii=False),
        status=status,
        content_type='application/json; charset=utf-8',
    )

def _err(status, message):
    return _ok({'success': False, 'error': message}, status=status)

def _get_interv():
    """Retourne l'intervenant lié à l'utilisateur connecté, le crée si absent."""
    user = request.env.user
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

def _fmt_mission(m):
    return {
        'id':                   m.id,
        'reference':            m.reference,
        'state':                m.state,
        'type_intervention':    m.type_intervention,
        'urgence':              m.urgence,
        'source':               m.source if hasattr(m, 'source') else '',
        'client':               m.client_id.name if m.client_id else '',
        'tel_sur_place':        m.tel_sur_place or '',
        'adresse':              m.adresse_intervention or '',
        'adresse_intervention': m.adresse_intervention or '',
        'date_rdv':             str(m.date_rdv) if m.date_rdv else None,
        'description':          m.description_sinistre or '',
        'description_sinistre': m.description_sinistre or '',
        'montant':              m.montant_devis or 0,
        'montant_devis':        m.montant_devis or 0,
        'reste_a_charge':       m.reste_a_charge or 0,
    }


class SinistreAPIController(http.Controller):

    # ── PING ─────────────────────────────────────────────────────────
    @http.route('/api/sinistre/v1/ping', type='http', auth='public',
                methods=['GET'], csrf=False)
    def ping(self, **kw):
        return _ok({'success': True, 'status': 'ok'})

    # ── ME ───────────────────────────────────────────────────────────
    @http.route('/api/sinistre/v1/me', type='http', auth='user',
                methods=['GET'], csrf=False)
    def me(self, **kw):
        user = request.env.user
        cr   = request.env.cr

        # Tout en SQL direct — contourne le cache ORM
        cr.execute("SELECT id, name, zone_intervention FROM sinistre_intervenant WHERE user_id = %s LIMIT 1", (user.id,))
        iv_row = cr.fetchone()
        if not iv_row:
            iv = _get_interv()
            cr.execute("SELECT id, name, zone_intervention FROM sinistre_intervenant WHERE id = %s", (iv.id,))
            iv_row = cr.fetchone()
        iv_id, iv_name, iv_zone = iv_row[0], iv_row[1] or user.name, iv_row[2] or ''

        cr.execute("SELECT phone, mobile FROM res_partner WHERE id = (SELECT partner_id FROM res_users WHERE id = %s)", (user.id,))
        pr = cr.fetchone() or ('', '')
        phone = pr[0] or pr[1] or ''

        membre_depuis = ''
        try:
            cd = user.create_date
            if cd:
                mois = {1:'Janvier',2:'Février',3:'Mars',4:'Avril',5:'Mai',6:'Juin',7:'Juillet',8:'Août',9:'Septembre',10:'Octobre',11:'Novembre',12:'Décembre'}
                membre_depuis = f"{mois.get(cd.month,'')} {cd.year}"
        except Exception:
            pass

        cr.execute("SELECT COUNT(*), COALESCE(SUM(montant_devis),0) FROM sinistre_mission WHERE intervenant_id=%s AND state IN ('termine','clos','facture')", (iv_id,))
        st = cr.fetchone() or (0, 0)
        nb_terminees, ca_total = st[0], float(st[1])

        from datetime import datetime
        now = datetime.now()
        cr.execute("SELECT COALESCE(SUM(montant_devis),0) FROM sinistre_mission WHERE intervenant_id=%s AND state IN ('termine','clos','facture') AND EXTRACT(month FROM date_cloture)=%s AND EXTRACT(year FROM date_cloture)=%s", (iv_id, now.month, now.year))
        ca_mois = float((cr.fetchone() or (0,))[0])

        specialites, specialites_types = [], []
        try:
            cr.execute("SELECT s.name, s.type_intervention FROM sinistre_specialite s JOIN sinistre_intervenant_sinistre_specialite_rel r ON r.sinistre_specialite_id=s.id WHERE r.sinistre_intervenant_id=%s", (iv_id,))
            for nom, ti in cr.fetchall():
                specialites.append(nom)
                if ti: specialites_types.append(ti)
        except Exception:
            pass

        certifications = []
        try:
            cr.execute("SELECT name, date_validite FROM sinistre_certification WHERE intervenant_id=%s ORDER BY sequence, id", (iv_id,))
            for nom, dv in cr.fetchall():
                certifications.append({'name': nom, 'date': f"Valide jusqu'en {dv.year}" if dv else 'À jour'})
        except Exception:
            pass

        return _ok({'success': True, 'user': {
            'uid': user.id, 'name': user.name, 'email': user.login,
            'phone': phone, 'company_name': iv_name, 'zone': iv_zone,
            'note_moyenne': 0, 'interventions': nb_terminees,
            'ca_total': ca_total, 'ca_mois': ca_mois,
            'specialites': specialites, 'specialites_types': specialites_types,
            'membre_depuis': membre_depuis, 'intervenant_id': iv_id,
            'certifications': certifications,
        }})


    @http.route('/api/sinistre/v1/intervenant/missions', type='http',
                auth='user', methods=['GET'], csrf=False)
    def mes_missions(self, **kw):
        iv = _get_interv()
        missions = request.env['sinistre.mission'].sudo().search([
            ('intervenant_id', '=', iv.id),
            ('state', 'not in', ('clos', 'annule')),
        ], order='urgence desc, date_rdv asc')
        return _ok({'success': True, 'missions': [_fmt_mission(m) for m in missions],
                    'total': len(missions)})

    # ── DÉTAIL MISSION (par ID ou référence) ─────────────────────────
    @http.route([
        '/api/sinistre/v1/mission/<int:mission_id>',
        '/api/sinistre/v1/mission/<string:reference>',
    ], type='http', auth='user', methods=['GET'], csrf=False)
    def get_mission(self, mission_id=None, reference=None, **kw):
        iv = _get_interv()
        domain = [('intervenant_id', '=', iv.id)]
        if mission_id:
            domain.append(('id', '=', mission_id))
        elif reference:
            domain.append(('reference', '=', reference))
        else:
            return _err(400, "ID ou référence requis")

        m = request.env['sinistre.mission'].sudo().search(domain, limit=1)
        if not m:
            return _err(404, "Mission introuvable")

        # Photos
        photos = []
        if hasattr(m, 'photo_ids'):
            photos = [{
                'id':          p.id,
                'type_photo':  p.type_photo,
                'description': p.description or '',
                'url':         f'/web/image/sinistre.photo/{p.id}/image',
            } for p in m.photo_ids]

        # Devis
        devis_data = None
        if hasattr(m, 'devis_ids') and m.devis_ids:
            d = m.devis_ids.sorted('id', reverse=True)[0]
            devis_data = {
                'id':            d.id,
                'state':         d.state,
                'montant_total': d.montant_total,
                'lignes': [{
                    'description':   l.description,
                    'quantite':      l.quantite,
                    'prix_unitaire': l.prix_unitaire,
                    'montant_total': l.montant_total,
                } for l in (d.ligne_ids if hasattr(d, 'ligne_ids') else [])],
            }

        data = _fmt_mission(m)
        data.update({'photos': photos, 'devis': devis_data})
        return _ok({'success': True, 'mission': data})

    # ── UPLOAD PHOTO ─────────────────────────────────────────────────
    @http.route('/api/sinistre/v1/intervenant/mission/<string:mission_id>/photo',
                type='http', auth='user', methods=['POST'], csrf=False)
    def upload_photo(self, mission_id, **kw):
        try: mission_id = int(mission_id)
        except: return _err(400, "ID invalide")
        try:
            data      = json.loads(request.httprequest.data or '{}')
            type_photo = data.get('type_photo', 'avant')
            image_b64  = data.get('image', '')
            description = data.get('description', '')

            if not image_b64:
                return _err(400, "Image manquante")

            m = request.env['sinistre.mission'].sudo().browse(mission_id)
            if not m.exists():
                return _err(404, "Mission introuvable")

            # Modèle photo si disponible
            if hasattr(request.env, '__getitem__') and 'sinistre.photo' in request.env:
                photo = request.env['sinistre.photo'].sudo().create({
                    'mission_id':  mission_id,
                    'type_photo':  type_photo,
                    'image':       image_b64,
                    'description': description,
                })
                return _ok({'success': True, 'photo_id': photo.id})
            else:
                # Fallback: stocker sur la mission directement
                return _ok({'success': True, 'photo_id': None,
                            'message': 'Photo reçue (stockage non configuré)'})
        except Exception as e:
            _logger.error(f"[sinistre] upload_photo: {e}")
            return _err(500, str(e))

    # ── DÉMARRER ─────────────────────────────────────────────────────
    @http.route('/api/sinistre/v1/intervenant/mission/<string:mission_id>/demarrer',
                type='http', auth='user', methods=['POST'], csrf=False)
    def demarrer(self, mission_id, **kw):
        try: mission_id = int(mission_id)
        except: return _err(400, "ID invalide")
        try:
            m = request.env['sinistre.mission'].sudo().browse(mission_id)
            if not m.exists():
                return _err(404, "Mission introuvable")
            m.write({'state': 'en_cours'})
            return _ok({'success': True, 'state': 'en_cours'})
        except Exception as e:
            return _err(500, str(e))

    # ── TERMINER ─────────────────────────────────────────────────────
    @http.route('/api/sinistre/v1/intervenant/mission/<string:mission_id>/terminer',
                type='http', auth='user', methods=['POST'], csrf=False)
    def terminer(self, mission_id, **kw):
        try: mission_id = int(mission_id)
        except: return _err(400, "ID invalide")
        try:
            from odoo.fields import Datetime
            m = request.env['sinistre.mission'].sudo().browse(mission_id)
            if not m.exists():
                return _err(404, "Mission introuvable")
            m.write({'state': 'termine', 'date_cloture': Datetime.now()})
            return _ok({'success': True, 'state': 'termine'})
        except Exception as e:
            return _err(500, str(e))

    # ── CRÉER DEVIS ──────────────────────────────────────────────────
    @http.route('/api/sinistre/v1/intervenant/mission/<string:mission_id>/devis',
                type='http', auth='user', methods=['POST'], csrf=False)
    def create_devis(self, mission_id, **kw):
        try:
            try: mission_id = int(mission_id)
            except: return _err(400, "ID invalide")

            data       = json.loads(request.httprequest.data or '{}')
            lignes     = data.get('ligne_ids', data.get('lignes', []))
            note       = data.get('note_client', data.get('note', ''))
            tva        = data.get('tva', 20.0)

            m = request.env['sinistre.mission'].sudo().browse(mission_id)
            if not m.exists():
                return _err(404, "Mission introuvable")

            devis = request.env['sinistre.devis'].sudo().create({
                'mission_id': mission_id,
                'note_client': note,
                'tva':         tva,
                'state':       'brouillon',
            })

            for l in lignes:
                request.env['sinistre.devis.ligne'].sudo().create({
                    'devis_id':      devis.id,
                    'description':   l.get('description', ''),
                    'quantite':      float(l.get('quantite', 1)),
                    'prix_unitaire': float(l.get('prix_unitaire', 0)),
                })

            return _ok({
                'success':  True,
                'devis_id': devis.id,
                'state':    'brouillon',
                'montant_ht':    devis.montant_ht,
                'montant_total': devis.montant_total,
            })
        except Exception as e:
            _logger.error(f"[sinistre] create_devis: {e}")
            return _err(500, str(e))

    # ── ENVOYER DEVIS ────────────────────────────────────────────────
    @http.route('/api/sinistre/v1/intervenant/devis/<string:devis_id>/envoyer',
                type='http', auth='user', methods=['POST'], csrf=False)
    def envoyer_devis(self, devis_id, **kw):
        try:
            try: devis_id = int(devis_id)
            except: return _err(400, "ID invalide")
            d = request.env['sinistre.devis'].sudo().browse(devis_id)
            if not d.exists():
                return _err(404, "Devis introuvable")
            d.write({'state': 'envoye'})
            return _ok({'success': True, 'state': 'envoye'})
        except Exception as e:
            return _err(500, str(e))

    # ── ACCEPTER DEVIS ───────────────────────────────────────────────
    @http.route('/api/sinistre/v1/intervenant/devis/<string:devis_id>/accepter',
                type='http', auth='user', methods=['POST'], csrf=False)
    def accepter_devis(self, devis_id, **kw):
        try:
            try: devis_id = int(devis_id)
            except: return _err(400, "ID invalide")
            d = request.env['sinistre.devis'].sudo().browse(devis_id)
            if not d.exists():
                return _err(404, "Devis introuvable")
            d.write({'state': 'accepte'})
            if d.mission_id:
                d.mission_id.write({'state': 'devis_accepte'})
            return _ok({'success': True, 'state': 'accepte'})
        except Exception as e:
            return _err(500, str(e))

    # ── REFUSER DEVIS ────────────────────────────────────────────────
    @http.route('/api/sinistre/v1/intervenant/devis/<string:devis_id>/refuser',
                type='http', auth='user', methods=['POST'], csrf=False)
    def refuser_devis(self, devis_id, **kw):
        try:
            try: devis_id = int(devis_id)
            except: return _err(400, "ID invalide")
            d = request.env['sinistre.devis'].sudo().browse(devis_id)
            if not d.exists():
                return _err(404, "Devis introuvable")
            d.write({'state': 'refuse'})
            return _ok({'success': True, 'state': 'refuse'})
        except Exception as e:
            return _err(500, str(e))

    # ── FCM TOKEN ────────────────────────────────────────────────────
    @http.route('/api/sinistre/v1/intervenant/fcm-token', type='http',
                auth='user', methods=['POST'], csrf=False)
    def fcm_token(self, **kw):
        try:
            data  = json.loads(request.httprequest.data or '{}')
            token = data.get('token', '')
            iv    = _get_interv()
            if iv and token:
                iv.write({'fcm_token': token})
            return _ok({'success': True})
        except Exception as e:
            return _err(500, str(e))

    # ── DEMANDE PUBLIQUE ─────────────────────────────────────────────
    @http.route('/api/sinistre/v1/mission', type='http', auth='public',
                methods=['POST'], csrf=False)
    def create_mission_public(self, **kw):
        try:
            data    = json.loads(request.httprequest.data or '{}')
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
