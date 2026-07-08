# models/trend_product.py (Minimum requis pour que trend_ad fonctionne,il faut modifier le modèle pour ajouter les champs nécessaires)
from odoo import models, fields

class TrendProduct(models.Model):
    _name = 'trend.product'
    _description = 'Produit'
    
    name = fields.Char(string='Nom')