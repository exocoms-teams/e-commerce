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

    # On ajoute un champ caché pour identifier facilement nos produits
    is_supplement = fields.Boolean(string="Est un complément alimentaire", default=True)

    @api.model
    def create(self, vals):
        # Automatisation Logistique : Si on crée un complément alimentaire
        if vals.get('is_supplement', True):
            # 1. On force le suivi par lot
            vals['tracking'] = 'lot'
            
            # 2. On active le suivi des dates de péremption
            vals['use_expiration_date'] = True
            
            # 3. On définit un temps de conservation par défaut
            if not vals.get('expiration_time'):
                vals['expiration_time'] = 365
                
        # On appelle la vraie méthode 'create' d'Odoo pour sauvegarder en base
        return super(ProductTemplate, self).create(vals)