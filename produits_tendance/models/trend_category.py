from odoo import fields, models


class TrendCategory(models.Model):
    _name = 'trend.category'
    _description = 'Catégorie de produit tendance'

    name = fields.Char(string="Nom", required=True)