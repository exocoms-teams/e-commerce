# -*- coding: utf-8 -*-
from odoo import api, fields, models, _
from odoo.exceptions import UserError


class BordereauMandat(models.Model):
    _name = 'bordereau.mandat'
    _description = 'Bordereau de Mandats de Paiement'
    _inherit = ['mail.thread', 'mail.activity.mixin']
    _order = 'name desc'

    name = fields.Char(
        string='Numéro de bordereau',
        readonly=True,
        default='/',
        copy=False,
        required=True,
    )
    date_bordereau = fields.Date(
        string='Date du bordereau',
        default=fields.Date.today,
        required=True,
        tracking=True,
    )
    exercice_budgetaire = fields.Integer(
        string='Exercice budgétaire',
        required=True,
        default=lambda self: fields.Date.today().year,
    )
    ordonnateur_id = fields.Many2one(
        'res.partner',
        string='Ordonnateur',
        required=True,
        tracking=True,
    )
    comptable_id = fields.Many2one(
        'res.partner',
        string='Comptable public',
        required=True,
        tracking=True,
    )
    mandat_ids = fields.One2many(
        'mandat.administratif',
        'bordereau_id',
        string='Mandats',
    )
    currency_id = fields.Many2one(
        'res.currency',
        default=lambda self: self.env.company.currency_id,
    )
    montant_total = fields.Monetary(
        string='Montant total',
        currency_field='currency_id',
        compute='_compute_totaux',
        store=True,
    )
    nombre_mandats = fields.Integer(
        string='Nombre de mandats',
        compute='_compute_totaux',
        store=True,
    )
    state = fields.Selection(
        [
            ('brouillon', 'Brouillon'),
            ('emis', 'Émis'),
            ('transmis', 'Transmis au comptable'),
            ('clos', 'Clôturé'),
        ],
        string='État',
        default='brouillon',
        tracking=True,
    )
    notes = fields.Text(string='Observations')
    company_id = fields.Many2one(
        'res.company',
        default=lambda self: self.env.company,
    )

    @api.depends('mandat_ids', 'mandat_ids.montant_net_payer')
    def _compute_totaux(self):
        for rec in self:
            rec.nombre_mandats = len(rec.mandat_ids)
            rec.montant_total = sum(rec.mandat_ids.mapped('montant_net_payer'))

    @api.model_create_multi
    def create(self, vals_list):
        for vals in vals_list:
            if vals.get('name', '/') == '/':
                vals['name'] = self.env['ir.sequence'].next_by_code('bordereau.mandat') or '/'
        return super().create(vals_list)

    def action_emettre(self):
        self.ensure_one()
        if not self.mandat_ids:
            raise UserError(_("Le bordereau doit contenir au moins un mandat."))
        mandats_invalides = self.mandat_ids.filtered(lambda m: m.state != 'ordonnancement')
        if mandats_invalides:
            raise UserError(_(
                "Tous les mandats doivent être ordonnancés avant d'émettre le bordereau.\n"
                "Mandats non conformes : %s"
            ) % ', '.join(mandats_invalides.mapped('name')))
        self.write({'state': 'emis'})

    def action_transmettre(self):
        self.ensure_one()
        if self.state != 'emis':
            raise UserError(_("Le bordereau doit être émis avant transmission."))
        self.mandat_ids.write({'state': 'prise_en_charge'})
        self.write({'state': 'transmis'})

    def action_cloturer(self):
        self.ensure_one()
        self.write({'state': 'clos'})

    def action_imprimer(self):
        return self.env.ref('mandat_administratif.action_report_bordereau_mandats').report_action(self)
