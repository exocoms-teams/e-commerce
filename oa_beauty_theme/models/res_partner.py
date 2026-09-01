from odoo import fields, models


class ResPartner(models.Model):
    _inherit = 'res.partner'

    # O&A Beauty Customer Profile Fields
    oa_skin_type = fields.Selection([
        ('normal', 'Normale'),
        ('dry', 'Sèche'),
        ('oily', 'Grasse'),
        ('combination', 'Mixte'),
        ('sensitive', 'Sensible'),
    ], string='Type de Peau', help='Le type de peau du client.')
    oa_skin_concern = fields.Selection([
        ('aging', 'Anti-âge'),
        ('acne', 'Acné'),
        ('hyperpigmentation', 'Hyperpigmentation'),
        ('dullness', 'Teint Terne'),
        ('redness', 'Rougeurs'),
        ('dehydration', 'Déshydratation'),
    ], string='Préoccupation Principale', help='La préoccupation cutanée principale du client.')
    oa_fragrance_preference = fields.Selection([
        ('floral', 'Florale'),
        ('woody', 'Boisée'),
        ('oriental', 'Orientale'),
        ('fresh', 'Fraîche'),
        ('gourmand', 'Gourmande'),
    ], string='Préférence Olfactive', help='La famille olfactive préférée du client.')
    oa_newsletter_optin = fields.Boolean(string='Inscrit Newsletter', default=False)
