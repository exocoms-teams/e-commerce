# -*- coding: utf-8 -*-
import json
from odoo import models, fields, api, _
from . import zone_utils


class SinistreIntervenant(models.Model):
    _name = 'sinistre.intervenant'
    _description = 'Intervenant / Artisan'
    _inherit = ['mail.thread', 'mail.activity.mixin']
    _rec_name = 'name'

    name = fields.Char(string='Nom', required=True, tracking=True)
    partner_id = fields.Many2one(
        'res.partner', string='Fiche Contact', required=True,
        help="Partenaire Odoo associé (pour facturation)",
    )
    user_id = fields.Many2one(
        'res.users', string='Compte Utilisateur',
        help="Compte pour accès à l'application mobile (PWA)",
    )

    # ── Spécialités ───────────────────────────────────────────────
    specialites = fields.Many2many('sinistre.specialite', string='Spécialités')
    zone_intervention = fields.Char(
        string="Zone d'Intervention",
        help="Codes postaux ou villes couverts (ex: 75, 92, 93...)",
    )

    # ── Contrat / Commission ─────────────────────────────────────
    taux_commission = fields.Float(
        string='Taux Commission Plateforme (%)',
        default=15.0,
        help="Pourcentage prélevé par la plateforme sur chaque intervention",
    )
    actif      = fields.Boolean(string='Actif',       default=True, tracking=True)
    disponible = fields.Boolean(string='Disponible',  default=True, tracking=True)
    note       = fields.Text(string='Notes Internes')

    # ── FCM / PWA ─────────────────────────────────────────────────
    fcm_token = fields.Char(
        string='Token FCM',
        help="Token Firebase pour les notifications push PWA",
        copy=False,
    )

    # ── Planning / Heures d'ouverture ────────────────────────────
    planning_slots = fields.Text(
        string="Créneaux Disponibles (JSON)",
        help="JSON {\"jour\": {\"heure\": bool}} — jour 0=dim, 1=lun…6=sam",
        copy=False,
    )
    absence_ids = fields.One2many(
        'sinistre.intervenant.absence', 'intervenant_id',
        string='Absences exceptionnelles',
    )

    # ── Coordonnées bancaires ─────────────────────────────────────
    iban             = fields.Char(string='IBAN',              copy=False)
    bic              = fields.Char(string='BIC / SWIFT',       copy=False)
    titulaire_compte = fields.Char(string='Titulaire du compte')
    banque           = fields.Char(string='Banque')

    # ── Stats ─────────────────────────────────────────────────────
    mission_ids       = fields.One2many('sinistre.mission', 'intervenant_id', string='Missions')
    certification_ids = fields.One2many('sinistre.certification', 'intervenant_id', string='Certifications')
    mission_count     = fields.Integer(compute='_compute_stats', string='Nb Missions')
    ca_total          = fields.Monetary(
        string='CA Total', compute='_compute_stats', currency_field='currency_id',
    )
    commission_due    = fields.Monetary(
        string='Commissions Dues', compute='_compute_stats', currency_field='currency_id',
    )
    currency_id = fields.Many2one(
        'res.currency', default=lambda self: self.env.company.currency_id,
    )

    @api.depends('mission_ids', 'mission_ids.state', 'mission_ids.montant_devis')
    def _compute_stats(self):
        for rec in self:
            missions_terminees = rec.mission_ids.filtered(
                lambda m: m.state in ('termine', 'facture', 'clos')
            )
            rec.mission_count  = len(rec.mission_ids)
            rec.ca_total       = sum(missions_terminees.mapped('montant_devis'))
            rec.commission_due = sum(missions_terminees.mapped('commission_plateforme'))

    # ── Helpers planning ─────────────────────────────────────────
    def get_planning_slots(self):
        """Retourne les slots sous forme de dict Python."""
        self.ensure_one()
        if self.planning_slots:
            try:
                return json.loads(self.planning_slots)
            except Exception:
                pass
        # Défaut : tout disponible (0–23h, 7 jours)
        return {str(d): {str(h): True for h in range(24)} for d in range(7)}

    def set_planning_slots(self, slots_dict):
        """Persiste les slots (dict Python → JSON)."""
        self.ensure_one()
        self.write({'planning_slots': json.dumps(slots_dict)})

    def couvre_adresse(self, adresse):
        """True si l'adresse mission est dans le secteur de l'artisan."""
        self.ensure_one()
        return zone_utils.adresse_dans_zone(adresse or '', self.zone_intervention or '')

    def action_voir_missions(self):
        return {
            'type': 'ir.actions.act_window',
            'name': f"Missions de {self.name}",
            'res_model': 'sinistre.mission',
            'view_mode': 'list,kanban,form',
            'domain': [('intervenant_id', '=', self.id)],
        }


class SinistreIntervenantAbsence(models.Model):
    _name = 'sinistre.intervenant.absence'
    _description = 'Absence Intervenant'
    _order = 'date_debut desc'

    intervenant_id = fields.Many2one(
        'sinistre.intervenant', string='Intervenant',
        required=True, ondelete='cascade',
    )
    date_debut = fields.Date(string='Date de début', required=True)
    date_fin   = fields.Date(string='Date de fin',   required=True)
    motif      = fields.Char(string='Motif')

    @api.constrains('date_debut', 'date_fin')
    def _check_dates(self):
        for rec in self:
            if rec.date_fin < rec.date_debut:
                raise models.ValidationError(
                    "La date de fin doit être postérieure à la date de début."
                )

    def _fmt(self):
        return {
            'id':         self.id,
            'date_debut': str(self.date_debut),
            'date_fin':   str(self.date_fin),
            'motif':      self.motif or '',
        }


class SinistreSpecialite(models.Model):
    _name = 'sinistre.specialite'
    _description = 'Spécialité Intervenant'

    name = fields.Char(string='Spécialité', required=True)
    type_intervention = fields.Selection([
        ('serrurerie',    'Serrurerie'),
        ('plomberie',     'Plomberie'),
        ('menuiserie_int','Menuiserie Intérieure'),
        ('menuiserie_ext','Menuiserie Extérieure'),
        ('vitrerie',      'Vitrerie'),
        ('electricite',   'Électricité'),
        ('autre',         'Autre'),
    ], string="Type d'Intervention")
    color = fields.Integer(string='Couleur', default=0)
