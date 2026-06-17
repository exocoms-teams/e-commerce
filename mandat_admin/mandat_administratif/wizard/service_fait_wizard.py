# -*- coding: utf-8 -*-
from odoo import api, fields, models, _
from odoo.exceptions import UserError


class ServiceFaitWizard(models.TransientModel):
    _name        = 'service.fait.wizard'
    _description = 'Certification du service fait'

    sale_order_id     = fields.Many2one('sale.order', required=True, readonly=True)
    mandat_numero     = fields.Char(related='sale_order_id.mandat_numero', readonly=True)
    amount_total      = fields.Monetary(related='sale_order_id.amount_total', readonly=True)
    currency_id       = fields.Many2one(related='sale_order_id.currency_id', readonly=True)

    date_service_fait     = fields.Date('Date de certification *', required=True, default=fields.Date.today)
    certificateur_nom     = fields.Char('Nom du certificateur *', required=True)
    certificateur_qualite = fields.Char('Qualité / Fonction *', required=True)

    nature_reception = fields.Selection([
        ('conforme',  'Réception conforme sans réserve'),
        ('reserves',  'Réception avec réserves'),
        ('partielle', 'Réception partielle'),
    ], required=True, default='conforme', string='Nature de la réception *')

    reserve_service_fait = fields.Text('Réserves / Observations')
    date_levee_reserves  = fields.Date('Date de levée des réserves')
    montant_certifie     = fields.Monetary('Montant certifié *', required=True, currency_field='currency_id')

    pv_attachment = fields.Binary('PV de réception (PDF)')
    pv_filename   = fields.Char('Nom du fichier')

    @api.model
    def default_get(self, fields_list):
        res = super().default_get(fields_list)
        so_id = self.env.context.get('default_sale_order_id')
        if so_id:
            so = self.env['sale.order'].browse(so_id)
            res['montant_certifie'] = so.amount_total
        return res

    def action_certifier(self):
        self.ensure_one()
        if self.nature_reception == 'reserves' and not self.reserve_service_fait:
            raise UserError(_('Vous devez renseigner les réserves.'))
        so = self.sale_order_id
        so.write({
            'service_fait_certifie':      True,
            'date_service_fait':          self.date_service_fait,
            'certificateur_service_fait': '%s – %s' % (self.certificateur_nom, self.certificateur_qualite),
            'reserve_service_fait':       self.reserve_service_fait,
            'mandat_state':               'service_fait',
        })
        if self.pv_attachment:
            self.env['ir.attachment'].create({
                'name': self.pv_filename or 'PV_reception.pdf',
                'type': 'binary', 'datas': self.pv_attachment,
                'res_model': 'sale.order', 'res_id': so.id,
            })
            for pj in so.pj_ids.filtered(lambda p: p.type_pj in ('service_fait', 'pv_reception')):
                pj.write({'fournie': True, 'date_reception': self.date_service_fait})
        return {'type': 'ir.actions.act_window', 'res_model': 'sale.order',
                'res_id': so.id, 'view_mode': 'form', 'target': 'current'}
