from odoo import fields, models

class Allergen(models.Model):
    _name = "allergen"
    _description = "Test Model"

    name = fields.Char()

    