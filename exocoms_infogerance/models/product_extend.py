from odoo import api, fields, models


class ProductTemplate(models.Model):
    _inherit = 'product.template'

    x_is_infogerance = fields.Boolean(
        'Service d\'infogérance',
        help="Cocher si ce produit est un service d'infogérance")
    x_infogerance_type = fields.Selection([
        ('subscription', 'Abonnement'),
        ('onetime', 'Intervention ponctuelle'),
        ('equipment', 'Équipement'),
    ], string='Type infogérance', default='subscription')
    x_billing_period = fields.Selection([
        ('monthly', 'Mensuel'),
        ('quarterly', 'Trimestriel'),
        ('yearly', 'Annuel'),
        ('onetime', 'Une fois'),
    ], string='Période de facturation', default='monthly')
