# -*- coding: utf-8 -*-
from odoo import fields, models, _
from odoo.exceptions import UserError


class PecWizard(models.TransientModel):
    _name        = 'pec.wizard'
    _description = 'Prise en charge comptable (PEC)'

    sale_order_id  = fields.Many2one('sale.order', required=True, readonly=True)
    mandat_numero  = fields.Char(related='sale_order_id.mandat_numero', readonly=True)
    amount_total   = fields.Monetary(related='sale_order_id.amount_total', readonly=True)
    currency_id    = fields.Many2one(related='sale_order_id.currency_id', readonly=True)

    decision = fields.Selection([
        ('acceptee',  'PEC acceptée'),
        ('rejetee',   'PEC rejetée'),
        ('suspendue', 'PEC suspendue (pièces complémentaires requises)'),
    ], required=True, default='acceptee', string='Décision du comptable *')

    date_pec          = fields.Date('Date de PEC *', required=True, default=fields.Date.today)
    reference_pec     = fields.Char('Référence PEC *', required=True)
    comptable_nom     = fields.Char('Nom du comptable *', required=True)
    motif_rejet       = fields.Text('Motif du rejet / suspension')
    pieces_demandees  = fields.Text('Pièces complémentaires demandées')
    date_limite       = fields.Date('Date limite pour les compléments')

    def action_valider(self):
        self.ensure_one()
        if self.decision == 'rejetee' and not self.motif_rejet:
            raise UserError(_('Renseignez le motif de rejet.'))
        if self.decision == 'suspendue' and not self.pieces_demandees:
            raise UserError(_('Précisez les pièces complémentaires demandées.'))
        so   = self.sale_order_id
        vals = {'date_pec': self.date_pec, 'reference_pec': self.reference_pec}
        if self.decision == 'acceptee':
            vals.update({'pec_acceptee': True, 'mandat_state': 'pec'})
        else:
            vals.update({
                'pec_acceptee':    False,
                'motif_rejet_pec': self.motif_rejet or self.pieces_demandees,
            })
        so.write(vals)
        return {'type': 'ir.actions.act_window', 'res_model': 'sale.order',
                'res_id': so.id, 'view_mode': 'form', 'target': 'current'}
