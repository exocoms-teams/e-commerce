from odoo import http
from odoo.http import request
import uuid

class AdvisorController(http.Controller):

    @http.route('/api/advisor/recommend', type='jsonrpc', auth='public', website=True)
    def get_recommendation(self, **kw):
        # Extract data from the JSON body
        data = request.jsonrequest
        skin_type = data.get('skin_type', '').lower()
        concern = data.get('main_concern', '').lower()
        budget = data.get('budget', '').lower()

        # Product Intelligence Layer: Query Odoo Catalog dynamically
        # In a real intelligent setup, we would score products. Here we do a basic matching.
        Product = request.env['product.template'].sudo()
        
        # Search all active skincare and makeup products published on website
        products = Product.search([('is_published', '=', True), ('sale_ok', '=', True)])
        
        recommended_ids = []
        routine_steps = []

        # Simple Scoring / Matching logic based on catalog data
        # Find a cleanser
        cleanser = products.filtered(lambda p: 'cleans' in (p.name or '').lower())
        if cleanser:
            recommended_ids.append(cleanser[0].id)
            routine_steps.append({'step': 'Step 1: Cleanse', 'product': cleanser[0].name, 'desc': 'Start by removing impurities.'})
            
        # Find a serum based on concern
        serum = False
        if concern in ['aging', 'dullness', 'hyperpigmentation']:
            serum = products.filtered(lambda p: 'vitamin c' in (p.name or '').lower())
        else:
            serum = products.filtered(lambda p: 'hydrat' in (p.name or '').lower() and 'serum' in (p.name or '').lower())
            
        if serum:
            recommended_ids.append(serum[0].id)
            routine_steps.append({'step': 'Step 2: Treat', 'product': serum[0].name, 'desc': 'Target your primary skin concerns.'})
            
        # Find a moisturizer
        moisturizer = products.filtered(lambda p: 'moisturizer' in (p.name or '').lower() or 'cream' in (p.name or '').lower())
        if moisturizer:
            recommended_ids.append(moisturizer[0].id)
            routine_steps.append({'step': 'Step 3: Moisturize', 'product': moisturizer[0].name, 'desc': 'Lock in hydration and protect the barrier.'})

        # Generate a unique session ID
        session_id = str(uuid.uuid4())

        # Save to Analytics Layer
        request.env['oa.advisor.session'].sudo().create({
            'session_id': session_id,
            'skin_type': skin_type,
            'main_concern': concern,
            'budget': budget,
            'recommended_product_ids': [(6, 0, recommended_ids)]
        })

        # Fetch product details for the frontend
        recommended_products_data = []
        for p_id in recommended_ids:
            p = Product.browse(p_id)
            recommended_products_data.append({
                'id': p.id,
                'name': p.name,
                'price': p.list_price,
                'url': p.website_url,
                'image_url': f'/web/image/product.template/{p.id}/image_128'
            })

        return {
            'status': 'success',
            'session_id': session_id,
            'explanation': f"Based on your profile (Skin Type: {skin_type}, Concern: {concern}), we have curated a routine to balance and nourish your skin.",
            'routine': routine_steps,
            'products': recommended_products_data
        }
