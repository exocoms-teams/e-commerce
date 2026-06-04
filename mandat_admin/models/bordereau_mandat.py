# -*- coding: utf-8 -*-
from odoo import models, fields, api, _
from odoo.exceptions import UserError


class BordereauMandat(models.Model):
    _name = 'bordereau.mandat'
    _description = 'Bordereau de Mandats'
    _inherit = ['mail.thread']
    _order = 'date_bordereau desc, name desc'

    name = fields.Char(
        string='Numéro de bordereau',
        readonly=True,
        copy=False,
        default='Nouveau',
    )
    date_bordereau = fields.Date(
        string='Date du bordereau',
        required=True,
        default=fields.Date.today,
        tracking=True,
    )
    collectivite_id = fields.Many2one(
        'res.company',
        string='Collectivité',
        required=True,
        default=lambda self: self.env.company,
    )
    ordonnateur_id = fields.Many2one(
        'res.users',
        string='Ordonnateur',
        required=True,
        default=lambda self: self.env.user,
    )
    mandat_ids = fields.One2many(
        'mandat.administratif',
        'bordereau_id',
        string='Mandats inclus',
    )
    nb_mandats = fields.Integer(
        string='Nombre de mandats',
        compute='_compute_totaux',
        store=True,
    )
    total_ttc = fields.Monetary(
        string='Total TTC',
        currency_field='currency_id',
        compute='_compute_totaux',
        store=True,
    )
    total_net = fields.Monetary(
        string='Total net à payer',
        currency_field='currency_id',
        compute='_compute_totaux',
        store=True,
    )
    currency_id = fields.Many2one(
        'res.currency',
        default=lambda self: self.env.ref('base.EUR'),
    )
    state = fields.Selection([
        ('brouillon', 'Brouillon'),
        ('emis', 'Émis'),
        ('transmis', 'Transmis au comptable'),
        ('cloture', 'Clôturé'),
    ], default='brouillon', string='État', tracking=True)

    note = fields.Text(string='Observations')

    @api.depends('mandat_ids', 'mandat_ids.montant_ttc', 'mandat_ids.montant_net')
    def _compute_totaux(self):
        for rec in self:
            rec.nb_mandats = len(rec.mandat_ids)
            rec.total_ttc = sum(rec.mandat_ids.mapped('montant_ttc'))
            rec.total_net = sum(rec.mandat_ids.mapped('montant_net'))

    def action_emettre(self):
        for rec in self:
            if not rec.mandat_ids:
                raise UserError(_('Le bordereau ne contient aucun mandat.'))
            if rec.name == 'Nouveau':
                rec.name = self.env['ir.sequence'].next_by_code('bordereau.mandat') or 'Nouveau'
            rec.state = 'emis'
            rec.message_post(body=_('Bordereau émis : %s mandats pour un total de %.2f €.') % (
                rec.nb_mandats, rec.total_net
            ))

    def action_transmettre(self):
        for rec in self:
            if rec.state != 'emis':
                raise UserError(_('Le bordereau doit être émis avant transmission.'))
            rec.state = 'transmis'
            mandats_valides = rec.mandat_ids.filtered(lambda m: m.state == 'valide')
            for m in mandats_valides:
                m.action_mandater()
            rec.message_post(body=_('Bordereau transmis au comptable.'))

    def action_cloturer(self):
        for rec in self:
            rec.state = 'cloture'

    def action_imprimer_bordereau(self):
        return self.env.ref('mandat_admin.action_report_bordereau').report_action(self)
