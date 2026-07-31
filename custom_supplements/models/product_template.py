from odoo import models, fields, api

class ProductTemplate(models.Model):
    _inherit = 'product.template'

    is_vegan = fields.Boolean(string="100% Vegan", default=False)
    nutritional_info = fields.Html(string="Valeurs Nutritionnelles")
    allergen_ids = fields.Many2many('allergen', string="Allergènes")
    is_supplement = fields.Boolean(string="Est un complément alimentaire", default=False)
    dosage = fields.Char(string="Dosage recommandé", help="Ex: 2 gélules par jour")
    ingredients = fields.Text(string="Ingrédients actifs", help="Liste des composants nutritionnels")

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

    def _search_get_detail(self, website, order, options):
        result = super()._search_get_detail(website, order, options)
        if options.get('allergens_exclude_ids'):
            result['base_domain'].append([('allergen_ids', 'not in', options['allergens_exclude_ids'])])
        return result
