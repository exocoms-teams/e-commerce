from odoo import models, fields, api

class ProductTemplate(models.Model):
    _inherit = 'product.template'

    is_vegan = fields.Boolean(string="100% Vegan", default=False)
    nutritional_info = fields.Html(string="Valeurs Nutritionnelles")
    allergens = fields.Char(string="Allergènes")
    
    is_supplement = fields.Boolean(string="Est un complément alimentaire", default=False)

    # CORRECTION : On utilise le décorateur 'multi' pour gérer les listes
    @api.model_create_multi
    def create(self, vals_list):
        # On fait une boucle pour analyser chaque produit de la liste
        for vals in vals_list:
            # Si le produit actuel est marqué comme complément
            if vals.get('is_supplement', False):
                vals['tracking'] = 'lot'
                vals['use_expiration_date'] = True
                
                if not vals.get('expiration_time'):
                    vals['expiration_time'] = 365
                    
        # On passe la liste modifiée à la vraie méthode d'Odoo
        return super(ProductTemplate, self).create(vals_list)