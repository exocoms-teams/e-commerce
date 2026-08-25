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

        xmlids = [
            # "stock_barcode.product_cable_management_box_2_product_template",  # Cable Management Box
            # "stock_barcode.product_custom_cabinet_metric_product_template",  # Customized Cabinet (Metric)
            # "stock_barcode.product_custom_cabinet_usa_product_template",  # Customized Cabinet (USA)
            # # "sale.advance_product_0_product_template",  # Deposit
            # "product.desk_pad_product_template",  # Desk Pad
            # "product.product_product_20_product_template",  # Flipover
            # "product.product_product_furniture_product_template",  # Furniture Assembly
            # "product.expense_hotel_product_template",  # Hotel Accommodation
            # "product.product_product_local_delivery_product_template",  # Local Delivery
            # "product.monitor_stand_product_template",  # Monitor Stand
            # "product.product_template_dining_table",  # Outdoor dining table
            # "product.expense_product_product_template",  # Restaurant Expenses
            # # "delivery.product_product_delivery_product_template",  # Standard delivery
            # # "delivery.product_product_delivery_poste_product_template",  # The Poste
            # "product.product_product_2_product_template",  # Virtual Home Staging
            # "product.product_product_1_product_template",  # Virtual Interior Design
        ]
        products = self.search([
            ("is_supplement", "=", False)
        ])

        _logger.info(
            "Nettoyage des produits de démonstration : %s produits",
            len(products),
        )

        products = products.filtered(
             lambda p: p.get_external_id().get(p.id) in xmlids
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