from odoo import models, fields, api

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

   # On passe le default à False. C'est au responsable de cocher la case pour tes compléments.
    is_supplement = fields.Boolean(string="Est un complément alimentaire", default=False)

    @api.model
    def create(self, vals):
        # On n'applique la logistique que si la case est cochée 
        # ET que le produit est de type 'product' (Article Stockable), pas un 'service'.
        if vals.get('is_supplement', False) and vals.get('type', 'consu') == 'product':
            vals['tracking'] = 'lot'
            vals['use_expiration_date'] = True
            
            if not vals.get('expiration_time'):
                vals['expiration_time'] = 365
                
        return super(ProductTemplate, self).create(vals)