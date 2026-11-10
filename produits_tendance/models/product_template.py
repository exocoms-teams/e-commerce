# models/product_template.py
"""WIN-66 : lien explicite entre un article d'abonnement et le groupe de
sécurité à attribuer une fois la facture validée (voir models/account_move.py).

Un champ dédié plutôt qu'un mapping en dur dans le code Python : ça permet à
un admin de créer/ajuster un tier depuis l'interface sans toucher au code, et
ça évite un `if product == ref('...') ` fragile dans le hook de facturation.
"""
from odoo import fields, models


class ProductTemplate(models.Model):
    _inherit = 'product.template'

    winners_subscription_group_id = fields.Many2one(
        comodel_name='res.groups',
        string="Groupe attribué (abonnement Winners)",
        help="Si renseigné, ce groupe est automatiquement attribué à "
             "l'utilisateur du client dès que la facture d'un abonnement "
             "sur cet article est validée (WIN-66).",
    )
