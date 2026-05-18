from odoo import models, fields


class ProductTemplateMarketplace(models.Model):
    """
    Extension du modele natif product.template.
    _inherit = heritage : on ETEND le modele existant sans le modifier.
    Odoo ajoute automatiquement la colonne vendor_id dans la table product_template.
    """
    _inherit = 'product.template'

    vendor_id = fields.Many2one(
        comodel_name='marketplace.vendor',
        string='Vendeur',
        ondelete='set null',   # si le vendeur est supprime, le champ devient vide (pas d'erreur)
        index=True,             # index SQL pour accelrer les recherches par vendeur
        help='Vendeur proprietaire de ce produit sur la marketplace'
    )
