from odoo import fields, models, api


class ProductTemplate(models.Model):
    _inherit = 'product.template'

    oa_type = fields.Char(string='Cosmetic Type', translate=True)
    oa_finish = fields.Char(string='Finish', translate=True)
    oa_best_for = fields.Char(string='Best For', translate=True)
    oa_key_ingredients = fields.Char(string='Key Ingredients', translate=True)
    oa_is_demo_product = fields.Boolean(
        string='Demo / Temporary Product',
        default=False,
        help='Marks temporary merchandising products that can be archived when the official supplier catalogue arrives.',
    )
    oa_skin_type = fields.Char(string='Skin Type', translate=True)
    oa_concern = fields.Char(string='Beauty Concern', translate=True)
    oa_routine_step = fields.Char(string='Routine Step', translate=True)
    oa_fragrance_family = fields.Char(string='Fragrance Family', translate=True)
    oa_occasion = fields.Char(string='Occasion', translate=True)
    
    # Fragrance & Expansion Fields
    oa_is_coming_soon = fields.Boolean(string='Coming Soon', default=False, help='If checked, the add to cart button will be replaced with a Coming Soon badge.')
    oa_fragrance_top_notes = fields.Char(string='Top Notes', translate=True, help='e.g., Bergamot, Mandarin, Pink Pepper')
    oa_fragrance_heart_notes = fields.Char(string='Heart Notes', translate=True, help='e.g., Rose, Jasmine, Orange Blossom')
    oa_fragrance_base_notes = fields.Char(string='Base Notes', translate=True, help='e.g., Vanilla, Musk, Sandalwood')
    oa_mood = fields.Char(string='Mood / Feeling', translate=True, help='e.g., Elegant, Sensual, Fresh')

    # SEO & Editorial Fields
    oa_benefits = fields.Html(string='Benefits', translate="html_translate", help='Long description of the product benefits.')
    oa_how_to_use = fields.Html(string='How to Use', translate="html_translate", help='Instructions on how to use the product.')
    oa_seo_keywords = fields.Char(string='SEO Keywords', translate=True, help='Comma-separated keywords for meta tags.')

    # Ingram Micro Fields
    oa_is_ingram_product = fields.Boolean(string='Is Ingram Product', default=False, readonly=True)
    oa_ingram_sku = fields.Char(string='Ingram SKU', readonly=True, index=True)

    def _oa_get_low_stock_qty(self):
        self.ensure_one()
        product_variant = self.product_variant_id
        if not product_variant or 'qty_available' not in product_variant._fields:
            return 0

        qty_available = product_variant.qty_available
        if qty_available and 0 < qty_available <= 5:
            return int(qty_available)
        return 0

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

    @api.model
    def cron_sync_ingram_catalog(self):
        """
        Scheduled action to fetch and sync products from Ingram Micro API.
        """
        import logging
        from ..utils.ingram_api_client import IngramApiClient
        _logger = logging.getLogger(__name__)
        _logger.info("Starting Ingram Micro Catalog Sync...")
        
        # Get settings
        get_param = self.env['ir.config_parameter'].sudo().get_param
        api_url = get_param('oa_beauty_theme.ingram_api_url')
        client_id = get_param('oa_beauty_theme.ingram_client_id')
        client_secret = get_param('oa_beauty_theme.ingram_client_secret')
        import_as_draft = get_param('oa_beauty_theme.ingram_import_as_draft', default='True') == 'True'
        
        if not api_url or not client_id or not client_secret:
            _logger.error("Ingram Micro API credentials not fully configured.")
            return False
            
        client = IngramApiClient(api_url, client_id, client_secret)
        products_data = client.fetch_catalog()
        
        if not products_data:
            _logger.warning("No products retrieved from Ingram Micro.")
            return True
            
        created_count = 0
        updated_count = 0
        
        for item in products_data:
            sku = item.get('ingramPartNumber')
            if not sku:
                continue
                
            existing_product = self.search([('oa_ingram_sku', '=', sku)], limit=1)
            
            vals = {
                'name': item.get('description', 'Unknown Ingram Product'),
                'default_code': sku,
                'list_price': item.get('customerPrice', 0.0),
                'standard_price': item.get('customerPrice', 0.0), # cost
                'type': 'product',
                'oa_is_ingram_product': True,
                'oa_ingram_sku': sku,
            }
            
            if existing_product:
                existing_product.write({'list_price': vals['list_price'], 'standard_price': vals['standard_price']})
                updated_count += 1
            else:
                vals['is_published'] = not import_as_draft
                self.create(vals)
                created_count += 1
                
        _logger.info("Ingram Sync Complete: %s created, %s updated.", created_count, updated_count)
        return True

    @api.model
    def clean_homepage_pages(self):
        """
        Deactivates any dynamically generated default homepages for OA Atelier
        to ensure our custom standalone homepage is routed correctly.
        """
        website = self.env.ref('oa_beauty_theme.oa_beauty_website', raise_if_not_found=False)
        if not website:
            return
        
        pages = self.env['website.page'].search([
            ('website_id', '=', website.id),
            ('url', '=', '/')
        ])
        
        our_page = self.env.ref('oa_beauty_theme.website_page_homepage', raise_if_not_found=False)
        for page in pages:
            if our_page and page.id != our_page.id:
                page.write({'active': False, 'is_homepage': False, 'url': '/old-home'})

