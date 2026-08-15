import base64

from odoo import fields, models, api
from odoo.modules.module import get_module_resource


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

    # Ingram Micro Fields
    oa_is_ingram_product = fields.Boolean(string='Is Ingram Product', default=False, readonly=True)
    oa_ingram_sku = fields.Char(string='Ingram SKU', readonly=True, index=True)

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
    def _oa_apply_production_catalog_defaults(self):
        """Fill only missing production fields for existing O&A catalog records."""
        defaults = {
            'product_serum_signature': {
                'image': 'static/src/img/product_placeholders/serum_signature.jpg',
                'website_meta_title': 'Serum Signature | Rituel Eclat | O&A Atelier',
                'website_meta_description': "Decouvrez Serum Signature, le soin eclat O&A Atelier a l'acide hyaluronique et rose de Damas pour une peau hydratee et lumineuse.",
            },
            'product_fond_de_teint_lumiere': {
                'image': 'static/src/img/oa_foundation.png',
                'website_meta_title': 'Fond de Teint Lumiere | Maquillage Soin | O&A Atelier',
                'website_meta_description': 'Un fond de teint lumiere a couvrance naturelle, pense pour unifier le teint sans masquer la peau.',
            },
            'product_baume_levres': {
                'image': 'static/src/img/product_placeholders/baume_levres.jpg',
                'website_meta_title': 'Baume Levres | Soin Couleur | O&A Atelier',
                'website_meta_description': 'Un baume levres nourrissant entre soin et couleur, formule avec beurre de karite et pigments naturels.',
            },
            'product_palette_regard': {
                'image': 'static/src/img/product_placeholders/palette_regard.jpg',
                'website_meta_title': 'Palette Regard | Ombres Nude Premium | O&A Atelier',
                'website_meta_description': 'Palette Regard O&A Atelier: douze teintes signature aux finis mats et satines pour des looks naturels ou intenses.',
            },
            'product_huile_corps': {
                'image': 'static/src/img/product_placeholders/huile_corps.jpg',
                'website_meta_title': 'Huile Corps | Soin Botanique | O&A Atelier',
                'website_meta_description': 'Huile Corps O&A Atelier, melange botanique de neuf huiles vegetales pour nourrir la peau et laisser un voile lumineux.',
            },
            'product_parfum_trinite': {
                'image': 'static/src/img/product_placeholders/parfum_trinite.jpg',
                'website_meta_title': 'Eau de Parfum Trinite | Fragrance O&A Atelier',
                'website_meta_description': 'Eau de Parfum Trinite, fragrance florale, boisee et musquee signee O&A Atelier.',
            },
            'product_oa_hydrating_serum': {'image': 'static/src/img/oa_serum_glow.png'},
            'product_oa_vitc_serum': {'image': 'static/src/img/product_placeholders/oa_vitc_serum.jpg'},
            'product_oa_daily_moisturizer': {'image': 'static/src/img/product_placeholders/oa_daily_moisturizer.jpg'},
            'product_oa_cleansing_foam': {'image': 'static/src/img/product_placeholders/oa_cleansing_foam.jpg'},
            'product_oa_night_repair': {'image': 'static/src/img/product_placeholders/oa_night_repair.jpg'},
            'product_oa_eye_recovery': {'image': 'static/src/img/product_placeholders/oa_eye_recovery.jpg'},
            'product_oa_velvet_foundation': {'image': 'static/src/img/oa_foundation.png'},
            'product_oa_matte_lipstick': {'image': 'static/src/img/product_placeholders/oa_matte_lipstick.jpg'},
            'product_oa_radiance_blush': {'image': 'static/src/img/product_placeholders/oa_radiance_blush.jpg'},
            'product_oa_glow_highlighter': {'image': 'static/src/img/product_placeholders/oa_glow_highlighter.jpg'},
            'product_oa_precision_mascara': {'image': 'static/src/img/product_placeholders/oa_precision_mascara.jpg'},
            'product_oa_nude_palette': {'image': 'static/src/img/product_placeholders/oa_nude_palette.jpg'},
        }

        for xmlid, vals in defaults.items():
            product = self.env.ref(f'oa_beauty_theme.{xmlid}', raise_if_not_found=False)
            if not product:
                continue
            write_vals = {}
            if not product.is_published:
                write_vals['is_published'] = True
            if not product.sale_ok:
                write_vals['sale_ok'] = True
            if vals.get('website_meta_title') and not product.website_meta_title:
                write_vals['website_meta_title'] = vals['website_meta_title']
            if vals.get('website_meta_description') and not product.website_meta_description:
                write_vals['website_meta_description'] = vals['website_meta_description']
            if vals.get('image') and not product.image_1920:
                image_path = get_module_resource('oa_beauty_theme', *vals['image'].split('/'))
                if image_path:
                    with open(image_path, 'rb') as image_file:
                        write_vals['image_1920'] = base64.b64encode(image_file.read())
            if write_vals:
                product.write(write_vals)

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

