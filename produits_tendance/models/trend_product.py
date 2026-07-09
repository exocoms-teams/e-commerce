from odoo import fields, models


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
    ], string="Source")