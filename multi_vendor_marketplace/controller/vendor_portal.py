# -*- coding: utf-8 -*-
from odoo import http
from odoo.http import request
from datetime import datetime


class VendorPortal(http.Controller):
    """Controleur du portail vendeur multi_vendor_marketplace"""

    def _get_vendor_or_redirect(self):
        """Recuperer le vendeur connecte ou None"""
        partner = request.env.user.partner_id
        website = request.website
        # Filtrer par site web actuel
        vendor = request.env['res.partner'].sudo().search([
            ('id', '=', partner.id),
            ('state', '=', 'Approved'),
        ], limit=1)
        return vendor if vendor else None

    @http.route('/vendor/dashboard', type='http',
                auth='user', website=True, sitemap=False)
    def vendor_dashboard(self, **kw):
        """Tableau de bord du vendeur"""
        vendor = self._get_vendor_or_redirect()
        if not vendor:
            return request.redirect('/shop')

        # Produits du vendeur
        # Produits du vendeur (filtre multi-website)
        website = request.website
        products = request.env['product.template'].sudo().search([
            ('seller_id', '=', vendor.id),
        ], order='name asc')

        # Commandes du mois
        first_day = datetime.now().replace(
            day=1, hour=0, minute=0, second=0)
        product_ids = products.mapped('product_variant_ids').ids
        orders_count = 0
        if product_ids:
            order_lines = request.env['sale.order.line'].sudo().search([
                ('product_id', 'in', product_ids),
                ('order_id.state', 'not in', ['cancel']),
                ('order_id.date_order', '>=', first_day),
            ])
            orders_count = len(order_lines.mapped('order_id'))

        return request.render(
            'multi_vendor_marketplace.vendor_portal_dashboard',
            {
                'vendor': vendor,
                'products': products,
                'orders_count': orders_count,
            }
        )

    @http.route('/vendor/products', type='http',
                auth='user', website=True, sitemap=False)
    def vendor_products(self, **kw):
        """Liste des produits du vendeur"""
        vendor = self._get_vendor_or_redirect()
        if not vendor:
            return request.redirect('/shop')
        website = request.website
        products = request.env['product.template'].sudo().search([
            ('seller_id', '=', vendor.id),
        ], order='name asc')
        return request.render(
            'multi_vendor_marketplace.vendor_portal_products',
            {'vendor': vendor, 'products': products}
        )

    @http.route('/vendor/product/<int:product_id>/edit',
                type='http', auth='user', website=True, sitemap=False)
    def vendor_product_edit(self, product_id, **kw):
        """Formulaire edition d'un produit"""
        vendor = self._get_vendor_or_redirect()
        if not vendor:
            return request.redirect('/shop')
        product = request.env['product.template'].sudo().browse(product_id)
        # Securite : le produit doit appartenir au vendeur
        if not product.exists() or product.seller_id.id != vendor.id:
            return request.redirect('/vendor/dashboard')
        error = kw.get('error')
        success = kw.get('success')
        return request.render(
            'multi_vendor_marketplace.vendor_portal_product_edit',
            {'vendor': vendor, 'product': product,
             'error': error, 'success': success}
        )

    @http.route('/vendor/product/<int:product_id>/save',
                type='http', auth='user', website=True,
                sitemap=False, methods=['POST'])
    def vendor_product_save(self, product_id, **kw):
        """Sauvegarder les modifications du produit"""
        vendor = self._get_vendor_or_redirect()
        if not vendor:
            return request.redirect('/shop')
        product = request.env['product.template'].sudo().browse(product_id)
        if not product.exists() or product.seller_id.id != vendor.id:
            return request.redirect('/vendor/dashboard')
        try:
            vals = {}
            if 'list_price' in kw:
                vals['list_price'] = float(kw['list_price'])
            if 'description_sale' in kw:
                vals['description_sale'] = kw['description_sale']
            product.write(vals)
        except Exception as e:
            return request.redirect(
                f'/vendor/product/{product_id}/edit?error={str(e)}')
        return request.redirect(
            f'/vendor/product/{product_id}/edit?success=1')

    @http.route('/vendor/orders', type='http',
                auth='user', website=True, sitemap=False)
    def vendor_orders(self, page=1, status=None, **kw):
        """Commandes du vendeur avec filtre et pagination"""
        vendor = self._get_vendor_or_redirect()
        if not vendor:
            return request.redirect('/shop')
        ITEMS_PER_PAGE = 10
        product_ids = request.env['product.template'].sudo().search(
            [('seller_id', '=', vendor.id)]
        ).mapped('product_variant_ids').ids
        domain = [
            ('product_id', 'in', product_ids),
            ('order_id.state', 'not in', ['cancel']),
        ]
        if status:
            domain.append(('order_id.state', '=', status))
        total = request.env['sale.order.line'].sudo().search_count(domain)
        total_orders = len(
            request.env['sale.order.line'].sudo().search(domain)
            .mapped('order_id')
        )
        offset = (int(page) - 1) * ITEMS_PER_PAGE
        orders = request.env['sale.order.line'].sudo().search(
            domain, order='order_id desc',
            limit=ITEMS_PER_PAGE, offset=offset
        )
        return request.render(
            'multi_vendor_marketplace.vendor_portal_orders',
            {'vendor': vendor, 'orders': orders,
             'total': total, 'total_orders': total_orders,
             'page': int(page), 'items_per_page': ITEMS_PER_PAGE,
             'status': status or ''}
        )
