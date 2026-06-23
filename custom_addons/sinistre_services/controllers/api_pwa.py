# -*- coding: utf-8 -*-
"""
api_pwa.py — Controller unique PWA / API Sinistre
Toutes les routes /api/sinistre/v1/ gérées ici.
"""
import json
import logging

from odoo import http, _
from odoo.http import request, Response
from odoo.exceptions import UserError

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

def _default_planning_slots():
    return {str(d): {str(h): True for h in range(24)} for d in range(7)}

def _db_column_exists(cr, table, column):
    cr.execute("""
        SELECT 1 FROM information_schema.columns
         WHERE table_name = %s AND column_name = %s
    """, (table, column))
    return bool(cr.fetchone())

def _db_table_exists(cr, table):
    cr.execute("""
        SELECT 1 FROM information_schema.tables WHERE table_name = %s
    """, (table,))
    return bool(cr.fetchone())

def _safe_planning_slots(intervenant):
    try:
        return intervenant.get_planning_slots()
    except Exception as e:
        _logger.warning("[sinistre] get_planning_slots ORM: %s", e)
    cr = intervenant.env.cr
    if _db_column_exists(cr, 'sinistre_intervenant', 'planning_slots'):
        try:
            cr.execute(
                "SELECT planning_slots FROM sinistre_intervenant WHERE id = %s",
                (intervenant.id,),
            )
            row = cr.fetchone()
            if row and row[0]:
                return json.loads(row[0])
        except Exception as e:
            _logger.warning("[sinistre] get_planning_slots SQL: %s", e)
    return _default_planning_slots()

def _safe_save_planning_slots(intervenant, slots):
    try:
        intervenant.set_planning_slots(slots)
        return
    except Exception as e:
        _logger.warning("[sinistre] set_planning_slots ORM: %s", e)
    cr = intervenant.env.cr
    if not _db_column_exists(cr, 'sinistre_intervenant', 'planning_slots'):
        raise ValueError(
            "Le module sinistre_services doit être mis à jour pour enregistrer le planning."
        )
    cr.execute(
        "UPDATE sinistre_intervenant SET planning_slots = %s, write_date = NOW() WHERE id = %s",
        (json.dumps(slots), intervenant.id),
    )

def _safe_absences(intervenant):
    from odoo.fields import Date
    today = Date.today()
    try:
        absences = intervenant.absence_ids.filtered(
            lambda a: a.date_fin and a.date_fin >= today
        )
        return [a._fmt() for a in absences.sorted('date_debut')]
    except Exception as e:
        _logger.warning("[sinistre] absence_ids ORM: %s", e)
    cr = intervenant.env.cr
    if not _db_table_exists(cr, 'sinistre_intervenant_absence'):
        return []
    try:
        cr.execute("""
            SELECT id, date_debut, date_fin, COALESCE(motif, '')
              FROM sinistre_intervenant_absence
             WHERE intervenant_id = %s AND date_fin >= %s
             ORDER BY date_debut
        """, (intervenant.id, today))
        return [
            {
                'id':         row[0],
                'date_debut': str(row[1]),
                'date_fin':   str(row[2]),
                'motif':      row[3] or '',
            }
            for row in cr.fetchall()
        ]
    except Exception as e:
        _logger.warning("[sinistre] absences SQL: %s", e)
        return []

def _intervenant_specialite_types(intervenant):
    """Retourne les types d'intervention couverts par les spécialités de l'intervenant."""
    types = []
    for s in (intervenant.specialites or []):
        if hasattr(s, 'type_intervention') and s.type_intervention:
            types.append(s.type_intervention)
    return types

def _mission_matches_specialites(mission, specialite_types):
    """True si la mission correspond aux spécialités (ou si aucune spécialité définie)."""
    if not specialite_types:
        return True
    return mission.type_intervention in specialite_types


def _enregistrer_proposition_reponse(intervenant, mission, reponse):
    """Enregistre la réponse d'un artisan à une proposition de mission."""
    from odoo import fields
    try:
        Proposition = request.env['sinistre.proposition.reponse'].sudo()
    except KeyError:
        _logger.warning("[sinistre] sinistre.proposition.reponse indisponible — mettre à jour le module")
        return
    except Exception as e:
        _logger.warning("[sinistre] proposition_reponse: %s", e)
        return
    existing = Proposition.search([
        ('intervenant_id', '=', intervenant.id),
        ('mission_id', '=', mission.id),
    ], limit=1)
    vals = {
        'intervenant_id': intervenant.id,
        'mission_id':     mission.id,
        'reponse':        reponse,
        'date_reponse':   fields.Datetime.now(),
    }
    if existing:
        existing.write(vals)
    else:
        Proposition.create(vals)


def _calc_taux_acceptation_jour(env, intervenant):
    """Taux acceptées / (acceptées + refusées) sur la journée en cours (UTC serveur)."""
    from datetime import datetime, time
    from odoo import fields

    try:
        Proposition = env['sinistre.proposition.reponse'].sudo()
    except KeyError:
        return None
    except Exception as e:
        _logger.warning("[sinistre] taux_acceptation_jour: %s", e)
        return None

    today = fields.Date.context_today(env)
    today_start = datetime.combine(today, time.min)

    reponses = Proposition.search([
        ('intervenant_id', '=', intervenant.id),
        ('date_reponse', '>=', fields.Datetime.to_string(today_start)),
    ])
    acceptes = len(reponses.filtered(lambda r: r.reponse == 'accepte'))
    refuses = len(reponses.filtered(lambda r: r.reponse == 'refuse'))
    total = acceptes + refuses
    if not total:
        return None
    return round(acceptes / total * 100, 1)


def _validate_devis_lignes(lignes):
    """Validation serveur des lignes de devis (description, quantité, prix)."""
    if not lignes:
        raise UserError(_("Au moins une ligne est requise"))
    for i, l in enumerate(lignes, start=1):
        desc = (l.get('description') or '').strip()
        if not desc:
            raise UserError(_("Ligne %s : description manquante") % i)
        try:
            prix = float(l.get('prix_unitaire', 0))
        except (TypeError, ValueError):
            raise UserError(_("Ligne %s : prix invalide") % i)
        if prix <= 0:
            raise UserError(_("Ligne %s : le prix doit être supérieur à 0") % i)
        try:
            qte = float(l.get('quantite', 1))
        except (TypeError, ValueError):
            raise UserError(_("Ligne %s : quantité invalide") % i)
        if qte <= 0:
            raise UserError(_("Ligne %s : la quantité doit être supérieure à 0") % i)


def _csv_response(filename, rows, headers):
    """Retourne une réponse HTTP CSV téléchargeable."""
    import csv
    import io
    buf = io.StringIO()
    writer = csv.writer(buf, delimiter=';')
    writer.writerow(headers)
    for row in rows:
        writer.writerow(row)
    return Response(
        buf.getvalue(),
        status=200,
        headers={
            'Content-Type': 'text/csv; charset=utf-8',
            'Content-Disposition': f'attachment; filename="{filename}"',
        },
    )


def _comptabilite_payload(intervenant):
    """Construit le payload comptabilité partagé entre GET et export."""
    from datetime import datetime
    from collections import defaultdict

    Mission = request.env['sinistre.mission'].sudo()
    missions = Mission.search([
        ('intervenant_id', '=', intervenant.id),
    ], order='date_cloture desc, date_rdv desc')

    taux = intervenant.taux_commission or 15.0
    pct = f"{taux:g} %"

    def _ville(adresse):
        if not adresse:
            return ''
        parts = adresse.split(',')
        return (parts[-1] if parts else adresse).strip().upper()

    def _statut(m):
        if m.state == 'annule':
            return 'Annulée'
        if m.state in ('termine', 'facture', 'clos'):
            return 'Succès'
        return 'En cours'

    def _facture_name(m):
        inv = m.facture_assurance_id or m.facture_client_id
        return inv.name if inv else ''

    def _categorie(m):
        if m.source in ('particulier', 'entreprise'):
            return 'b2c'
        if m.urgence in ('urgente', 'tres_urgente'):
            return 'du'
        return 'travaux'

    factures = {'du': [], 'travaux': [], 'b2c': []}
    detail_solde = {'du': [], 'travaux': [], 'b2c': []}
    ca_par_annee = defaultdict(float)
    virements_map = defaultdict(lambda: {
        'montant_solde': 0.0, 'commission': 0.0,
        'montant_paye': 0.0, 'rac_facture': 0.0, 'ca_genere': 0.0,
    })

    for m in missions:
        cat = _categorie(m)
        row = {
            'id':           m.id,
            'reference':    m.reference,
            'ville':        _ville(m.adresse_intervention),
            'statut':       _statut(m),
            'date_rdv':     str(m.date_rdv) if m.date_rdv else '',
            'date_cloture': str(m.date_cloture) if m.date_cloture else '',
            'facture':      _facture_name(m),
            'a_facturer':   (
                m.state in ('termine', 'facture', 'clos')
                and not _facture_name(m)
            ),
            'beneficiaire': (m.client_id.name or '').upper(),
            'dossier_du':   m.ref_assurance or m.reference or '',
        }
        if cat in factures:
            factures[cat].append(row)

        if m.state in ('termine', 'facture', 'clos') and m.date_cloture:
            dt = m.date_cloture
            ca_par_annee[dt.year] += m.montant_devis or 0
            key = dt.strftime('%Y-%m')
            v = virements_map[key]
            montant = m.montant_devis or 0
            comm = m.commission_plateforme or (montant * taux / 100)
            v['montant_solde'] += montant
            v['commission'] += comm
            v['montant_paye'] += max(montant - comm, 0)
            v['rac_facture'] += m.reste_a_charge or 0
            v['ca_genere'] += montant

            if cat in detail_solde and _facture_name(m):
                tva = 1.2
                detail_solde[cat].append({
                    'dossier':          m.reference,
                    'numero_facture':   _facture_name(m),
                    'date_facturation': str(dt.date()) if dt else '',
                    'montant_ht':       round(montant / tva, 2),
                    'montant_ttc':      montant,
                })

    terminees = missions.filtered(
        lambda m: m.state in ('termine', 'facture', 'clos')
    )
    commission_due = sum(terminees.mapped('commission_plateforme'))
    solde = -round(commission_due, 2)

    pending = terminees.filtered(
        lambda m: not m.facture_assurance_id and not m.facture_client_id
    )
    factures_a_fournir = [{
        'id':                m.id,
        'reference':         m.reference,
        'date':              str(m.date_cloture or m.date_rdv or ''),
        'client':            m.client_id.name if m.client_id else '',
        'type_intervention': m.type_intervention,
        'prestation':        m.description_sinistre or '',
        'adresse':           m.adresse_intervention or '',
        'montant_devis':     m.montant_devis or 0,
        'source':            m.source or '',
        'a_facturer':        True,
    } for m in pending]

    current_year = datetime.now().year
    ca_list = [
        {'annee': y, 'montant': round(ca_par_annee.get(y, 0), 2)}
        for y in range(current_year, current_year - 7, -1)
    ]

    virements = []
    for key in sorted(virements_map.keys(), reverse=True):
        dt = datetime.strptime(key + '-01', '%Y-%m-%d')
        v = virements_map[key]
        virements.append({
            'date':          dt.strftime('%d/%m/%Y') + ' à 01:00',
            'montant_solde': round(v['montant_solde'], 2),
            'commission':    round(v['commission'], 2),
            'montant_paye':  round(v['montant_paye'], 2),
            'rac_facture':   round(v['rac_facture'], 2),
            'ca_genere':     round(v['ca_genere'], 2),
        })

    commissions = [
        {'type': 'Mesures conservatoires', 'intervention': pct, 'pieces': '—', 'total_ht': pct},
        {'type': 'Travaux',                'intervention': pct, 'pieces': '—', 'total_ht': pct},
        {'type': 'B2C',                    'intervention': pct, 'pieces': '—', 'total_ht': pct},
    ]

    return {
        'taux_commission':    taux,
        'solde':              solde,
        'commissions':        commissions,
        'ca_par_annee':       ca_list,
        'virements':          virements,
        'factures':           factures,
        'detail_solde':       detail_solde,
        'factures_a_fournir': factures_a_fournir,
    }


def _fmt_mission(m):
    inv = m.facture_assurance_id or m.facture_client_id
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
        'date_cloture':         str(m.date_cloture) if m.date_cloture else None,
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
        'facture_numero':       inv.name if inv else '',
        'a_facturer':           (
            m.state in ('termine', 'facture', 'clos')
            and not m.facture_assurance_id
            and not m.facture_client_id
        ),
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
        if not iv:
            return _err(403, "Accès non autorisé")

        try:
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
            admin_phone = request.env['ir.config_parameter'].sudo().get_param(
                'sinistre.admin_phone', '0X0X0X'
            )

            Mission = request.env['sinistre.mission'].sudo()
            taux_acceptation = _calc_taux_acceptation_jour(request.env, iv)

            terminees_sans_facture = Mission.search([
                ('intervenant_id', '=', iv.id),
                ('state', 'in', ('termine', 'facture', 'clos')),
            ]).filtered(
                lambda m: not m.facture_assurance_id and not m.facture_client_id
            )
            commission_due = sum(
                m.commission_plateforme or 0
                for m in Mission.search([
                    ('intervenant_id', '=', iv.id),
                    ('state', 'in', ('termine', 'facture', 'clos')),
                ])
            )

            return _ok({'success': True, 'user': {
                'uid':               user.id,
                'name':              user.name,
                'email':             user.login,
                'phone':             phone,
                'street':            partner.street or '',
                'street2':           partner.street2 or '',
                'city':              partner.city or '',
                'zip':               partner.zip or '',
                'company_name':      entreprise,
                'admin_phone':       admin_phone,
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
                'solde_comptabilite': -round(commission_due, 2),
                'taux_acceptation':  taux_acceptation,
                'factures_a_fournir': len(terminees_sans_facture),
            }})
        except Exception as e:
            _logger.error("[sinistre] me: %s", e, exc_info=True)
            return _err(500, str(e))

    # ── MES MISSIONS ─────────────────────────────────────────────────
    @http.route(f'{PREFIX}/intervenant/missions', type='http',
                auth='user', methods=['GET'], csrf=False)
    def mes_missions(self, **kw):
        iv = _get_intervenant()
        if not iv:
            return _err(403, "Accès non autorisé")
        historique = str(kw.get('historique', '')).lower() in ('1', 'true', 'yes')
        if historique:
            domain = [
                ('intervenant_id', '=', iv.id),
                ('state', 'in', ('termine', 'facture', 'clos')),
            ]
            order = 'date_cloture desc, date_rdv desc'
        else:
            domain = [
                ('intervenant_id', '=', iv.id),
                ('state', 'not in', ('clos', 'annule')),
            ]
            order = 'urgence desc, date_rdv asc'
        missions = request.env['sinistre.mission'].sudo().search(domain, order=order)
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
            mission.message_post(body=_("✅ Signature après intervention enregistrée."))
            return _ok({'success': True, 'facture': bool(
                mission.facture_assurance_id or mission.facture_client_id
            )})
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
        try:
            _validate_devis_lignes(lignes)
        except UserError as e:
            return _err(400, e.args[0] if e.args else str(e))
        existing = request.env['sinistre.devis'].sudo().search([
            ('mission_id', '=', mission.id),
        ], limit=1)
        if existing:
            return _err(400, "Un devis existe déjà pour cette mission")
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
        try:
            _validate_devis_lignes(lignes)
        except UserError as e:
            return _err(400, e.args[0] if e.args else str(e))
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
            # Accusé de réception plateforme (max 1 par 30 min)
            from datetime import timedelta
            from odoo import fields
            recent_platform = request.env['sinistre.message'].sudo().search([
                ('mission_id', '=', mission.id),
                ('auteur_type', '=', 'plateforme'),
                ('date_envoi', '>=', fields.Datetime.now() - timedelta(minutes=30)),
            ], limit=1)
            if not recent_platform:
                request.env['sinistre.message'].sudo().create({
                    'mission_id':  mission.id,
                    'auteur_type': 'plateforme',
                    'auteur_nom':  'Plateforme FairFair',
                    'contenu':     _(
                        "Votre message a bien été reçu. Un conseiller vous répondra "
                        "dans les meilleurs délais."
                    ),
                    'lu_artisan':  False,
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
        ], order='urgence desc, date_reception asc', limit=50)
        specialite_types = _intervenant_specialite_types(intervenant)
        if specialite_types:
            missions = missions.filtered(
                lambda m: _mission_matches_specialites(m, specialite_types)
            )[:20]
        else:
            missions = missions[:20]
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
        specialite_types = _intervenant_specialite_types(intervenant)
        if specialite_types and not _mission_matches_specialites(mission, specialite_types):
            return _err(403, "Cette mission ne correspond pas à vos spécialités")
        try:
            mission.sudo().write({'intervenant_id': intervenant.id, 'state': 'assigne'})
            mission.message_post(body=_(f"✅ Mission acceptée par {intervenant.name}."))
            _enregistrer_proposition_reponse(intervenant, mission, 'accepte')
            return _ok({
                'success': True,
                'state': mission.state,
                'mission_id': mission.id,
                'taux_acceptation': _calc_taux_acceptation_jour(request.env, intervenant),
            })
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
            _enregistrer_proposition_reponse(intervenant, mission, 'refuse')
            return _ok({
                'success': True,
                'taux_acceptation': _calc_taux_acceptation_jour(request.env, intervenant),
            })
        except Exception as e:
            return _err(500, str(e))

    # ── FACTURER MISSION ─────────────────────────────────────────────
    @http.route(f'{PREFIX}/intervenant/mission/<int:mission_id>/facturer',
                type='http', auth='user', methods=['POST'], csrf=False)
    def facturer_mission(self, mission_id, **kwargs):
        intervenant = _get_intervenant()
        if not intervenant:
            return _err(403, "Accès non autorisé")
        mission = _check_mission(intervenant, mission_id)
        if not mission:
            return _err(404, "Mission introuvable")
        try:
            facture = mission.sudo().action_generer_facture()
            numero = facture.name if facture else _fmt_mission(mission)['facture_numero']
            return _ok({
                'success':        True,
                'facture_numero': numero or '',
                'mission':        _fmt_mission(mission),
            })
        except UserError as e:
            return _err(400, e.args[0] if e.args else str(e))
        except Exception as e:
            _logger.error(f"[sinistre] facturer_mission: {e}", exc_info=True)
            return _err(400, str(e))

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
            slots = _safe_planning_slots(intervenant)
            return _ok({
                'success':  True,
                'slots':    slots,
                'absences': _safe_absences(intervenant),
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
            _safe_save_planning_slots(intervenant, slots)
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
            Absence = request.env['sinistre.intervenant.absence'].sudo()
            try:
                Absence.create({
                    'intervenant_id': intervenant.id,
                    'date_debut':     date_debut,
                    'date_fin':       date_fin,
                    'motif':          motif,
                })
            except Exception as orm_err:
                _logger.warning("[sinistre] absence_add ORM: %s", orm_err)
                cr = request.env.cr
                if not _db_table_exists(cr, 'sinistre_intervenant_absence'):
                    raise ValueError(
                        "Le module sinistre_services doit être mis à jour pour enregistrer les absences."
                    ) from orm_err
                cr.execute("""
                    INSERT INTO sinistre_intervenant_absence
                        (intervenant_id, date_debut, date_fin, motif, create_date, write_date)
                    VALUES (%s, %s, %s, %s, NOW(), NOW())
                """, (intervenant.id, date_debut, date_fin, motif or ''))
            return _ok({'success': True,
                        'absences': _safe_absences(intervenant)})
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
            try:
                absence.unlink()
            except Exception as orm_err:
                _logger.warning("[sinistre] absence_delete ORM: %s", orm_err)
                cr = request.env.cr
                cr.execute("""
                    DELETE FROM sinistre_intervenant_absence
                     WHERE id = %s AND intervenant_id = %s
                """, (absence_id, intervenant.id))
                if not cr.rowcount:
                    return _err(404, "Absence introuvable ou accès interdit")
            return _ok({'success': True, 'absences': _safe_absences(intervenant)})
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

    # ── FACTURES À FOURNIR ───────────────────────────────────────────
    @http.route(f'{PREFIX}/intervenant/factures-a-fournir',
                type='http', auth='user', methods=['GET'], csrf=False)
    def factures_a_fournir(self, **kw):
        intervenant = _get_intervenant()
        if not intervenant:
            return _err(403, "Accès non autorisé")
        try:
            missions = request.env['sinistre.mission'].sudo().search([
                ('intervenant_id', '=', intervenant.id),
                ('state', 'in', ('termine', 'facture', 'clos')),
            ], order='date_cloture desc, date_rdv desc')
            pending = missions.filtered(
                lambda m: not m.facture_assurance_id and not m.facture_client_id
            )
            rows = [{
                'id':                   m.id,
                'reference':            m.reference,
                'date':                 str(m.date_cloture or m.date_rdv or ''),
                'client':               m.client_id.name if m.client_id else '',
                'type_intervention':    m.type_intervention,
                'prestation':           m.description_sinistre or '',
                'adresse':              m.adresse_intervention or '',
                'montant_devis':        m.montant_devis or 0,
                'source':               m.source or '',
                'a_facturer':           True,
            } for m in pending]
            return _ok({'success': True, 'factures': rows, 'count': len(rows)})
        except Exception as e:
            _logger.error(f"[sinistre] factures_a_fournir: {e}", exc_info=True)
            return _err(500, str(e))

    @http.route(f'{PREFIX}/intervenant/comptabilite',
                type='http', auth='user', methods=['GET'], csrf=False)
    def comptabilite_get(self, **kw):
        intervenant = _get_intervenant()
        if not intervenant:
            return _err(403, "Accès non autorisé")
        try:
            payload = _comptabilite_payload(intervenant)
            return _ok({'success': True, **payload})
        except Exception as e:
            _logger.error(f"[sinistre] comptabilite_get: {e}", exc_info=True)
            return _err(500, str(e))

    @http.route(f'{PREFIX}/intervenant/comptabilite/export',
                type='http', auth='user', methods=['GET'], csrf=False)
    def comptabilite_export(self, **kw):
        intervenant = _get_intervenant()
        if not intervenant:
            return _err(403, "Accès non autorisé")
        try:
            export_type = kw.get('type', 'factures')
            tab = kw.get('tab', 'du')
            payload = _comptabilite_payload(intervenant)

            if export_type == 'virements':
                rows = [
                    [v['date'], v['montant_solde'], v['commission'],
                     v['montant_paye'], v['rac_facture'], v['ca_genere']]
                    for v in payload['virements']
                ]
                return _csv_response(
                    'virements.csv',
                    rows,
                    ['Date', 'Montant soldé', 'Commission', 'Montant payé',
                     'RAC facturé', 'CA généré'],
                )

            if export_type == 'detail':
                rows = []
                for cat in ('du', 'travaux', 'b2c'):
                    for r in payload['detail_solde'].get(cat, []):
                        rows.append([
                            cat.upper(), r['dossier'], r['numero_facture'],
                            r['date_facturation'], r['montant_ht'], r['montant_ttc'],
                        ])
                return _csv_response(
                    'detail_solde.csv',
                    rows,
                    ['Catégorie', 'Dossier', 'N° facture', 'Date',
                     'Montant HT', 'Montant TTC'],
                )

            if export_type == 'factures_a_fournir':
                rows = [
                    [f['reference'], f['date'], f['client'], f['type_intervention'],
                     f['prestation'], f['montant_devis']]
                    for f in payload['factures_a_fournir']
                ]
                return _csv_response(
                    'factures_a_fournir.csv',
                    rows,
                    ['Référence', 'Date', 'Client', 'Type', 'Prestation', 'Montant devis'],
                )

            rows_data = payload['factures'].get(tab, [])
            if tab == 'travaux':
                rows = [
                    [r['id'], r['dossier_du'], r['beneficiaire'], r['ville'],
                     r['statut'], 'Oui' if r['a_facturer'] else 'Non']
                    for r in rows_data
                ]
                headers = ['ID', 'Dossier DU', 'Bénéficiaire', 'Ville', 'Statut', 'À facturer']
            else:
                rows = [
                    [r['id'], r['ville'], r['statut'],
                     r['date_rdv'] or r['date_cloture'], r['facture'] or 'À facturer']
                    for r in rows_data
                ]
                headers = ['ID', 'Ville', 'Statut', 'Date RDV', 'Facture']
            return _csv_response(f'factures_{tab}.csv', rows, headers)
        except Exception as e:
            _logger.error(f"[sinistre] comptabilite_export: {e}", exc_info=True)
            return _err(500, str(e))

    @http.route(f'{PREFIX}/intervenant/comptabilite/commissions',
                type='http', auth='user', methods=['GET'], csrf=False)
    def comptabilite_commissions(self, **kw):
        intervenant = _get_intervenant()
        if not intervenant:
            return _err(403, "Accès non autorisé")
        try:
            from datetime import datetime
            annee = int(kw.get('annee', datetime.now().year))
            trim = kw.get('trimestre', 'T1').upper()
            trim_map = {
                'T1': (1, 3), 'T2': (4, 6), 'T3': (7, 9), 'T4': (10, 12),
            }
            mois_debut, mois_fin = trim_map.get(trim, (1, 3))
            taux = intervenant.taux_commission or 15.0

            missions = request.env['sinistre.mission'].sudo().search([
                ('intervenant_id', '=', intervenant.id),
                ('state', 'in', ('termine', 'facture', 'clos')),
            ])
            rows = []
            for m in missions:
                if not m.date_cloture:
                    continue
                if m.date_cloture.year != annee:
                    continue
                if not (mois_debut <= m.date_cloture.month <= mois_fin):
                    continue
                montant = m.montant_devis or 0
                comm = m.commission_plateforme or round(montant * taux / 100, 2)
                inv = m.facture_assurance_id or m.facture_client_id
                rows.append([
                    m.reference,
                    str(m.date_cloture.date()) if m.date_cloture else '',
                    m.client_id.name if m.client_id else '',
                    montant,
                    comm,
                    inv.name if inv else '',
                ])

            return _csv_response(
                f'commissions_{trim}_{annee}.csv',
                rows,
                ['Référence mission', 'Date clôture', 'Client',
                 'Montant TTC', 'Commission plateforme', 'N° facture'],
            )
        except Exception as e:
            _logger.error(f"[sinistre] comptabilite_commissions: {e}", exc_info=True)
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
