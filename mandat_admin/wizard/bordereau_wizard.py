# -*- coding: utf-8 -*-
from odoo import api, fields, models, _
from odoo.exceptions import UserError


class BordereauWizard(models.TransientModel):
    _name        = 'bordereau.wizard'
    _description = "Création d'un bordereau de mandats"

    date_debut       = fields.Date('Période du *', required=True)
    date_fin         = fields.Date('Au *', required=True)
    ordonnateur      = fields.Char('Ordonnateur *', required=True)
    comptable_public = fields.Char('Comptable public assignataire *', required=True)
    note             = fields.Text('Observations')
    auto_select      = fields.Boolean(
        'Sélectionner automatiquement les mandats de la période', default=True)
    invoice_ids      = fields.Many2many(
        'account.move', string='Factures à inclure',
        domain=[('is_mandat_administratif', '=', True), ('move_type', '=', 'out_invoice')])

    @api.onchange('date_debut', 'date_fin', 'auto_select')
    def _onchange_auto(self):
        if self.auto_select and self.date_debut and self.date_fin:
            self.invoice_ids = self.env['account.move'].search([
                ('is_mandat_administratif', '=', True),
                ('move_type', '=', 'out_invoice'),
                ('invoice_date', '>=', self.date_debut),
                ('invoice_date', '<=', self.date_fin),
                ('state', '=', 'posted'),
            ])

    def action_creer(self):
        self.ensure_one()
        if not self.invoice_ids:
            raise UserError(_('Aucune facture sélectionnée.'))
        b = self.env['mandat.bordereau'].create({
            'date_emission':   fields.Date.today(),
            'date_debut':      self.date_debut,
            'date_fin':        self.date_fin,
            'ordonnateur':     self.ordonnateur,
            'comptable_public': self.comptable_public,
            'invoice_ids':     [(6, 0, self.invoice_ids.ids)],
            'note':            self.note,
        })
        b.action_emettre()
        return {'type': 'ir.actions.act_window', 'name': _('Bordereau de mandats'),
                'res_model': 'mandat.bordereau', 'res_id': b.id,
                'view_mode': 'form', 'target': 'current'}
