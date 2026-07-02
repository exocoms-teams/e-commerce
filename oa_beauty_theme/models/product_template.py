from odoo import fields, models, api


class ProductTemplate(models.Model):
    _inherit = 'product.template'

    oa_type = fields.Char(string='Cosmetic Type')
    oa_finish = fields.Char(string='Finish')
    oa_best_for = fields.Char(string='Best For')
    oa_key_ingredients = fields.Char(string='Key Ingredients')
    
    # Fragrance & Expansion Fields
    oa_is_coming_soon = fields.Boolean(string='Coming Soon', default=False, help='If checked, the add to cart button will be replaced with a Coming Soon badge.')
    oa_fragrance_top_notes = fields.Char(string='Top Notes', help='e.g., Bergamot, Mandarin, Pink Pepper')
    oa_fragrance_heart_notes = fields.Char(string='Heart Notes', help='e.g., Rose, Jasmine, Orange Blossom')
    oa_fragrance_base_notes = fields.Char(string='Base Notes', help='e.g., Vanilla, Musk, Sandalwood')
    oa_mood = fields.Char(string='Mood / Feeling', help='e.g., Elegant, Sensual, Fresh')

    # SEO & Editorial Fields
    oa_benefits = fields.Html(string='Benefits', help='Long description of the product benefits.')
    oa_how_to_use = fields.Html(string='How to Use', help='Instructions on how to use the product.')
    oa_seo_keywords = fields.Char(string='SEO Keywords', help='Comma-separated keywords for meta tags.')
    @api.model
    def _archive_default_demo_products(self):
        """
        Archives Odoo default demo furniture products so they don't pollute the luxury theme.
        We only match common demo keywords to avoid accidentally archiving the user's real products.
        """
        demo_keywords = [
            'Desk', 'Chair', 'Acoustic', 'Cabinet', 'Bin', 'Drawer', 'Lamp', 'Pedestal',
            'Conference', 'Table', 'Whiteboard', 'Storage', 'Bose', 'E-Com', 'Cable', 'Screen',
            'Bureau', 'Chaise', 'Poubelle', 'Tiroir', 'Lampe', 'Caisson', 'Conférence', 'Tableau',
            'Lorem Ipsum', 'Placeholder', 'Demo', 'Sample Product', 'Test Product'
        ]
        
        domain = ['|'] * (len(demo_keywords) - 1)
        for kw in demo_keywords:
            domain.append(('name', 'ilike', kw))
            
        products = self.search(domain)
        if products:
            products.write({'active': False, 'is_published': False})
