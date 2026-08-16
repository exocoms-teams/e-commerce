from odoo import fields, models


class OASearchLog(models.Model):
    _name = 'oa.search.log'
    _description = 'O&A Search Analytics'
    _order = 'create_date desc'

    query = fields.Char(required=True, index=True)
    normalized_query = fields.Char(index=True)
    result_count = fields.Integer(default=0)
    is_zero_result = fields.Boolean(index=True)
    event_type = fields.Selection(
        [
            ('search', 'Search'),
            ('autocomplete', 'Autocomplete'),
            ('product_click', 'Product Click'),
            ('category_click', 'Category Click'),
        ],
        default='search',
        required=True,
        index=True,
    )
    product_id = fields.Many2one('product.template', ondelete='set null')
    category_id = fields.Many2one('product.public.category', ondelete='set null')
    website_id = fields.Many2one('website', ondelete='set null')
    session_id = fields.Char(index=True)
