from odoo import models, fields, api
from odoo.exceptions import ValidationError

class TrendProduct(models.Model):
    _name = 'trend.product'
    _description = 'Produit collecté sur un site e-commerce'

    name = fields.Char(string="Nom du produit", required=True)
    product_ref = fields.Char(string="Référence produit (site source)")
    category_id = fields.Many2one('trend.category', string="Catégorie")
    sales_count = fields.Integer(string="Nombre de ventes")
    date = fields.Date(string="Date de collecte")
    score_site_x = fields.Float(string="Score site source")
    country = fields.Char(string="Pays")

    
    source = fields.Selection([
        ('scraping', 'Scraping'),
        ('crowdsourcing', 'Crowdsourcing'),
        ('api', 'API'),
    ], string="Source", required=True, default='api')

    ad_ids = fields.One2many(
        'trend.ad',
        'product_id',
        string="Publicités liées"
    )

    # --- CONTRAINTES SQL ---
    _sql_constraints = [
        (
            'product_ref_source_uniq', 
            'unique(product_ref, source)', 
            'Ce produit (référence + source) est déjà enregistré. Impossible de le dupliquer.'
        )
    ]

    # --- MÉTHODES DE VALIDATION ---
    @api.constrains('sales_count')
    def _check_sales_count_positive(self):
        for record in self:
            if record.sales_count is not None and record.sales_count < 0:
                raise ValidationError(
                    "Le nombre de ventes (sales_count) ne peut pas être négatif."
                )