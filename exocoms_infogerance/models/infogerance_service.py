from odoo import api, fields, models, _


class InfogeranceService(models.Model):
    _name = 'exocoms.infogerance.service'
    _description = 'Service d\'infogérance souscrit'
    _rec_name = 'product_id'
    _order = 'contract_id, sequence'

    contract_id = fields.Many2one('exocoms.infogerance.contract',
                                  string='Contrat', required=True,
                                  ondelete='cascade')
    sequence = fields.Integer('Séquence', default=10)
    product_id = fields.Many2one('product.product',
                                 string='Service', required=True,
                                 domain=[('type', '=', 'service'),
                                         ('x_is_infogerance', '=', True)])
    name = fields.Char('Description', related='product_id.name',
                       readonly=True)
    quantity = fields.Integer('Quantité', default=1, required=True)
    unit_price = fields.Monetary('Prix unitaire', currency_field='currency_id')
    subtotal = fields.Monetary('Total', compute='_compute_subtotal',
                               currency_field='currency_id', store=True)
    currency_id = fields.Many2one('res.currency',
                                  related='contract_id.company_id.currency_id')
    notes = fields.Text('Notes')

    @api.depends('quantity', 'unit_price')
    def _compute_subtotal(self):
        for s in self:
            s.subtotal = s.quantity * (s.unit_price or 0.0)

    @api.onchange('product_id')
    def _onchange_product_id(self):
        if self.product_id:
            self.unit_price = self.product_id.list_price
