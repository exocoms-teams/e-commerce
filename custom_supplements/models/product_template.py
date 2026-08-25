from odoo import api, fields, models
from odoo.fields import Domain
import logging

_logger = logging.getLogger(__name__)

class ProductTemplate(models.Model):
    _inherit = 'product.template'

    is_vegan = fields.Boolean(string='100% Vegan', default=False)
    nutritional_info = fields.Html(string='Valeurs nutritionnelles')
    
    # Attention: Vérifie que ton modèle s'appelle bien 'allergen' et pas 'custom_supplements.allergen'
    allergen_ids = fields.Many2many('allergen', string='Allergènes') 
    
    is_supplement = fields.Boolean(string='Complément alimentaire', default=False)
    dosage = fields.Char(string='Dosage recommandé', help='Exemple : 2 gélules par jour')
    ingredients = fields.Text(string='Ingrédients actifs')

    @api.model_create_multi
    def create(self, vals_list):
        for vals in vals_list:
            if vals.get('is_supplement'):
                vals.setdefault('tracking', 'lot')
                vals.setdefault('use_expiration_date', True)
                vals.setdefault('expiration_time', 365)
                vals.setdefault('is_storable', True)
                vals.setdefault('alert_time', 30)

        return super().create(vals_list)

    def write(self, vals):
        # On n'applique ces valeurs par défaut que si on est en train de passer le produit en "Complément"
        if vals.get("is_supplement"):
            vals.setdefault('tracking', 'lot')
            vals.setdefault('use_expiration_date', True)
            vals.setdefault('expiration_time', 365)
            vals.setdefault('is_storable', True)
            vals.setdefault('alert_time', 30)
        return super().write(vals)

    def _search_get_detail(self, website, order, options):
        result = super()._search_get_detail(website, order, options)
        allergen_ids = options.get('allergens_exclude_ids')
        
        if allergen_ids:
            filtre_allergenes = [('allergen_ids', 'not in', allergen_ids)]
            # Syntaxe propre et moderne (Odoo 18/19+)
            result['search_extra'] = Domain(result.get('search_extra', [])) & Domain(filtre_allergenes)
            
        return result

    @api.onchange("is_supplement")
    def _onchange_is_supplement(self):
        if self.is_supplement:
            self.is_storable = True


    def _archive_demo_products(self):
        config = self.env["ir.config_parameter"].sudo()

        if config.get_param("custom_supplements.demo_products_cleaned"):
            return

        products = self.search([
            ("is_supplement", "=", False),
            ("is_published", "=", True),
        ])

        _logger.info(
            "Nettoyage des produits de démonstration : %s produits",
            len(products),
        )

        for product in products:
            _logger.info(
                "Archivage : [%s] %s",
                product.id,
                product.name,
            )

        products.write({
            "active": False,
            "is_published": False,
        })

        config.set_param(
            "custom_supplements.demo_products_cleaned",
            "1",
        )

        _logger.info("Nettoyage des produits de démonstration terminé.")