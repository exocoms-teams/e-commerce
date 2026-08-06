from odoo import fields, models


class Allergen(models.Model):
    _name = 'allergen'
    _description = 'Allergen'
    _order = 'name'

    name = fields.Char(required=True, index=True)
    active = fields.Boolean(default=True)
