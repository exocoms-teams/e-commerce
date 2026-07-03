from odoo import models, fields

class ProductTemplate(models.Model):
    # L'héritage: 
    _inherit = 'product.template'

    # Ajout des nouveaux champs spécifiques aux compléments alimentaires
    is_vegan = fields.Boolean(string="100% Vegan", default=False)
    
    # Tableau des macros (Protéines, Glucides...)
    nutritional_info = fields.Html(string="Valeurs Nutritionnelles")
    
    # Un champ  pour les allergènes
    allergens = fields.Char(
        string="Allergènes", 
        help="Indiquez ici les allergènes présents (ex: Lait, Soja, Arachides)"
    )