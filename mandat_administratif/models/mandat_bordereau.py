# -*- coding: utf-8 -*-
from odoo import api, fields, models, _
from odoo.exceptions import UserError


class MandatBordereau(models.Model):
    """Bordereau récapitulatif des mandats signé par l'ordonnateur."""
    _name        = 'mandat.bordereau'
    _description = 'Bordereau de mandats administratifs'
    _inherit     = ['mail.thread', 'mail.activity.mixin']
    _order       = 'date_emission desc, name desc'

    name = fields.Char('N° bordereau', readonly=True, copy=False, default='Nouveau')

    company_id       = fields.Many2one('res.company', default=lambda s: s.env.company)
    date_emission    = fields.Date('Date émission', default=fields.Date.today, required=True)
    date_debut       = fields.Date('Période du', required=True)
    date_fin         = fields.Date('Au',         required=True)
    ordonnateur      = fields.Char('Ordonnateur', required=True)
    comptable_public = fields.Char('Comptable public assignataire', required=True)

    state = fields.Selection([
        ('draft',    'Brouillon'),
        ('emis',     'Émis'),
        ('signe',    'Signé'),
        ('transmis', 'Transmis au comptable'),
        ('acquitte', 'Acquitté'),
    ], default='draft', tracking=True)

    invoice_ids = fields.Many2many(
        'account.move',
        'bordereau_invoice_rel', 'bordereau_id', 'invoice_id',
        string='Mandats inclus',
        domain=[('is_mandat_administratif', '=', True)],
    )

    montant_total  = fields.Monetary('Montant total TTC',
                                     compute='_compute_totaux', store=True,
                                     currency_field='currency_id')
    nombre_mandats = fields.Integer('Nombre de mandats',
                                    compute='_compute_totaux', store=True)
    currency_id    = fields.Many2one('res.currency',
                                     default=lambda s: s.env.company.currency_id)

    note               = fields.Text('Observations')
    date_signature     = fields.Date('Date de signature')
    date_transmission  = fields.Date('Date de transmission')

    @api.depends('invoice_ids', 'invoice_ids.amount_total')
    def _compute_totaux(self):
        for b in self:
            b.montant_total  = sum(b.invoice_ids.mapped('amount_total'))
            b.nombre_mandats = len(b.invoice_ids)

    def action_emettre(self):
        for b in self:
            if not b.invoice_ids:
                raise UserError(_('Sélectionnez au moins un mandat.'))
            if b.name == 'Nouveau':
                b.name = self.env['ir.sequence'].next_by_code('mandat.bordereau') or 'BORD/???'
            b.state = 'emis'

    def action_signer(self):
        self.write({'state': 'signe', 'date_signature': fields.Date.today()})

    def action_transmettre(self):
        self.write({'state': 'transmis', 'date_transmission': fields.Date.today()})

    def action_acquitter(self):
        self.write({'state': 'acquitte'})

    def action_print(self):
        return self.env.ref('mandat_administratif.action_report_bordereau').report_action(self)
