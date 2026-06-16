# -*- coding: utf-8 -*-
from odoo import http
from odoo.http import request


class BoatServicesController(http.Controller):

    def _get_boat_products(self):
        return request.env['product.template'].sudo().search([
            ('is_boat_product', '=', True),
            ('sale_ok', '=', True),
        ], order='sequence, name')

    @http.route(['/boats'], type='http', auth='public', website=True, sitemap=True)
    def boat_list(self, **kwargs):
        products = self._get_boat_products()
        return request.render('boat_services.boat_list_page', {
            'products': products,
        })

    @http.route(['/boats/<int:product_id>'], type='http', auth='public', website=True, sitemap=True)
    def boat_detail(self, product_id, **kwargs):
        product = request.env['product.template'].sudo().browse(product_id)
        if not product.exists() or not product.is_boat_product:
            return request.not_found()

        return request.render('boat_services.boat_detail_page', {
            'product': product,
        })

    @http.route([
        '/boats/request-price',
        '/boats/request-price/<int:product_id>',
    ], type='http', auth='public', website=True, sitemap=False)
    def request_price_form(self, product_id=None, **kwargs):
        product = False
        if product_id:
            product = request.env['product.template'].sudo().browse(product_id)
            if not product.exists() or not product.is_boat_product:
                product = False

        countries = request.env['res.country'].sudo().search([])
        products = self._get_boat_products()

        return request.render('boat_services.boat_inquiry_form_page', {
            'inquiry_type': 'price',
            'product': product,
            'products': products,
            'countries': countries,
        })

    @http.route('/boats/catalog', type='http', auth='public', website=True, sitemap=True)
    def catalog_form(self, **kwargs):
        countries = request.env['res.country'].sudo().search([])
        products = self._get_boat_products()
        return request.render('boat_services.boat_inquiry_form_page', {
            'inquiry_type': 'catalog',
            'product': False,
            'products': products,
            'countries': countries,
        })

    @http.route('/boats/contact', type='http', auth='public', website=True, sitemap=True)
    def contact_form(self, **kwargs):
        countries = request.env['res.country'].sudo().search([])
        products = self._get_boat_products()
        return request.render('boat_services.boat_inquiry_form_page', {
            'inquiry_type': 'contact',
            'product': False,
            'products': products,
            'countries': countries,
        })

    @http.route('/boats/inquiry/submit', type='http', auth='public', methods=['POST'], website=True, csrf=True)
    def submit_inquiry(self, **post):
        product_id = post.get('product_id')
        country_id = post.get('country_id')

        vals = {
            'inquiry_type': post.get('inquiry_type') or 'price',
            'customer_name': post.get('customer_name'),
            'customer_email': post.get('customer_email'),
            'customer_phone': post.get('customer_phone'),
            'customer_company': post.get('customer_company'),
            'message': post.get('message'),
            'budget': post.get('budget'),
        }

        if product_id:
            vals['product_id'] = int(product_id)
        if country_id:
            vals['country_id'] = int(country_id)
        if post.get('expected_date'):
            vals['expected_date'] = post.get('expected_date')
        if post.get('passenger_count'):
            vals['passenger_count'] = int(post.get('passenger_count'))

        request.env['boat.inquiry'].sudo().create(vals)

        return request.render('boat_services.boat_thank_you_page', {
            'inquiry_type': vals['inquiry_type'],
        })
