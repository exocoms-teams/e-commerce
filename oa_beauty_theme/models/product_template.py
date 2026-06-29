from odoo import fields, models, api


class ProductTemplate(models.Model):
    _inherit = 'product.template'

    oa_type = fields.Char(string='Cosmetic Type')
    oa_finish = fields.Char(string='Finish')
    oa_best_for = fields.Char(string='Best For')
    oa_key_ingredients = fields.Char(string='Key Ingredients')

    @api.model
    def _archive_default_demo_products(self):
        """
        Archives Odoo default demo furniture products so they don't pollute the luxury theme.
        We only match common demo keywords to avoid accidentally archiving the user's real products.
        """
        demo_keywords = [
            'Desk', 'Chair', 'Acoustic', 'Cabinet', 'Bin', 'Drawer', 'Lamp', 'Pedestal',
            'Conference', 'Table', 'Whiteboard', 'Storage', 'Bose', 'E-Com', 'Cable', 'Screen',
            'Lorem Ipsum', 'Placeholder', 'Demo', 'Sample Product', 'Test Product'
        ]
        
        domain = ['|'] * (len(demo_keywords) - 1)
        for kw in demo_keywords:
            domain.append(('name', 'ilike', kw))
            
        products = self.search(domain)
        if products:
            products.write({'active': False, 'is_published': False})
