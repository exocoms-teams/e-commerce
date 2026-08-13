from odoo import models, fields

class AdvisorSession(models.Model):
    _name = 'oa.advisor.session'
    _description = 'Beauty Advisor Analytics Session'
    _order = 'create_date desc'

    session_id = fields.Char(string='Session ID', required=True)
    skin_type = fields.Char(string='Skin Type')
    main_concern = fields.Char(string='Main Concern')
    makeup_preference = fields.Char(string='Makeup Preference')
    budget = fields.Char(string='Budget')
    recommended_product_ids = fields.Many2many('product.template', string='Recommended Products')
