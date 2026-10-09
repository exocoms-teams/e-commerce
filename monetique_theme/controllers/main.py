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

    @http.route('/devis', type='http', auth='public', website=True, sitemap=True)
    def devis(self, **kw):
        website = request.env['website'].get_current_website()
        products = request.env['product.template'].search(
            website.sale_product_domain()
        )
        return request.render('monetique_theme.page_devis', {'products': products})

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

    @http.route('/devis/submit', type='http', auth='public', methods=['POST'], website=True, csrf=True)
    def devis_submit(self, **post):
        website = request.env['website'].get_current_website()
        product = request.env['product.template']
        try:
            product_id = int(post.get('product_id', 0))
        except (TypeError, ValueError):
            product_id = 0

        if product_id:
            product = product.search(
                [('id', '=', product_id)] + website.sale_product_domain(), limit=1
            )

        product_name = product.name if product else 'Produit non renseigné'
        quantity = post.get('quantity') or 'Non renseignée'
        description = (
            'Produit souhaité : %s\n'
            'Quantité : %s\n'
            'Société : %s\n\n'
            'Besoins spécifiques :\n%s'
        ) % (
            product_name,
            quantity,
            post.get('company') or 'Non renseignée',
            post.get('notes') or 'Aucun',
        )

        request.env['crm.lead'].sudo().create({
            'name': 'Demande de devis - %s' % (post.get('name') or 'Site web'),
            'type': 'opportunity',
            'contact_name': post.get('name'),
            'email_from': post.get('email'),
            'phone': post.get('phone'),
            'partner_name': post.get('company'),
            'description': description,
        })
        return request.redirect('/devis?submitted=1')
