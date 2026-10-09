from odoo import http
from odoo.http import request


class Monetique(http.Controller):

    @http.route('/', type='http', auth='public', website=True, sitemap=True)
    def home(self, **kw):
        website = request.env['website'].get_current_website()
        products = request.env['product.template'].search(
            website.sale_product_domain(), limit=8
        )
        return request.render('monetique_theme.page_home', {'products': products})

    @http.route('/services', type='http', auth='public', website=True, sitemap=True)
    def services(self, **kw):
        return request.render('monetique_theme.page_services', {})

    def _create_opportunity(self, values, source):
        """Create an opportunity from a website form submission."""
        contact_name = values.get('name') or values.get('contact_name')
        subject = values.get('subject') or '%s - %s' % (
            source, contact_name or 'Site web'
        )
        description = values.get('message') or values.get('description') or values.get('details')

        request.env['crm.lead'].sudo().create({
            'name': subject,
            'type': 'opportunity',
            'contact_name': contact_name,
            'email_from': values.get('email') or values.get('email_from'),
            'phone': values.get('phone') or values.get('mobile'),
            'description': description,
        })

    @http.route('/contact/submit', type='http', auth='public', methods=['POST'], website=True, csrf=True)
    def contact_submit(self, **post):
        self._create_opportunity(post, 'Demande de contact')
        return request.redirect('/contactus?submitted=1')

    @http.route('/audit/request', type='http', auth='public', methods=['POST'], website=True, csrf=True)
    def audit_request(self, **post):
        self._create_opportunity(post, "Demande d'audit")
        return request.redirect('/services?audit_submitted=1')
