# -*- coding: utf-8 -*-
from odoo import models, fields, api, _


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
    actif = fields.Boolean(string='Actif', default=True, tracking=True)
    disponible = fields.Boolean(string='Disponible', default=True, tracking=True)
    note = fields.Text(string='Notes Internes')

    # ── FCM / PWA ─────────────────────────────────────────────────
    fcm_token = fields.Char(
        string='Token FCM',
        help="Token Firebase pour les notifications push PWA",
        copy=False,
    )

    # ── Stats ─────────────────────────────────────────────────────
    mission_ids       = fields.One2many('sinistre.mission', 'intervenant_id', string='Missions')
    certification_ids = fields.One2many('sinistre.certification', 'intervenant_id', string='Certifications')
    mission_count = fields.Integer(compute='_compute_stats', string='Nb Missions')
    ca_total = fields.Monetary(
        string='CA Total', compute='_compute_stats', currency_field='currency_id',
    )
    commission_due = fields.Monetary(
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
            rec.mission_count = len(rec.mission_ids)
            rec.ca_total = sum(missions_terminees.mapped('montant_devis'))
            rec.commission_due = sum(missions_terminees.mapped('commission_plateforme'))

    def action_voir_missions(self):
        return {
            'type': 'ir.actions.act_window',
            'name': f"Missions de {self.name}",
            'res_model': 'sinistre.mission',
            'view_mode': 'list,kanban,form',
            'domain': [('intervenant_id', '=', self.id)],
        }


class SinistreSpecialite(models.Model):
    _name = 'sinistre.specialite'
    _description = 'Spécialité Intervenant'

    name = fields.Char(string='Spécialité', required=True)
    type_intervention = fields.Selection([
        ('serrurerie', 'Serrurerie'),
        ('plomberie', 'Plomberie'),
        ('menuiserie_int', 'Menuiserie Intérieure'),
        ('menuiserie_ext', 'Menuiserie Extérieure'),
        ('vitrerie', 'Vitrerie'),
        ('electricite', 'Électricité'),
        ('autre', 'Autre'),
    ], string="Type d'Intervention")
    color = fields.Integer(string='Couleur', default=0)
