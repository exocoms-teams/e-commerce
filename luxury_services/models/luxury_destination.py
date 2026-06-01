from odoo import models, fields

class LuxuryDestination(models.Model):
    _name= 'luxury.destination'
    _description = 'Destination Luxury'
    _order = 'name'


    name = fields.Char(string = 'Destination', required=True)
    pays_id = fields.Many2one('res.country', string = 'Pays')
    description = fields.Text(string = 'Description')
    active = fields.Boolean(default=True)