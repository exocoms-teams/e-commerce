from odoo import http
from odoo.http import request

class OABeautyController(http.Controller):

    @http.route('/shop/category/makeup', type='http', auth='public', website=True)
    def makeup_category(self, **kw):
        # Chercher la catégorie Maquillage/Makeup par nom de manière permissive
        category = request.env['product.public.category'].sudo().search([
            '|', ('name', 'ilike', 'makeup'), ('name', 'ilike', 'maquill')
        ], limit=1)
        
        if category:
            # Rediriger vers l'URL officielle Odoo qui gère la catégorie
            return request.redirect('/shop/category/%s' % category.id)
            
        # Si la catégorie n'est pas trouvée, rediriger vers la boutique globale
        return request.redirect('/shop')

    @http.route('/shop/category/skincare', type='http', auth='public', website=True)
    def skincare_category(self, **kw):
        # Chercher la catégorie Soin/Skincare
        category = request.env['product.public.category'].sudo().search([
            '|', ('name', 'ilike', 'skincare'), ('name', 'ilike', 'soin')
        ], limit=1)
        
        if category:
            return request.redirect('/shop/category/%s' % category.id)
            
        return request.redirect('/shop')

    @http.route('/shop/category/fragrances', type='http', auth='public', website=True)
    def fragrances_category(self, **kw):
        category = request.env['product.public.category'].sudo().search([
            '|', ('name', 'ilike', 'fragrance'), ('name', 'ilike', 'parfum')
        ], limit=1)
        if category:
            return request.redirect('/shop/category/%s' % category.id)
        return request.redirect('/shop')
