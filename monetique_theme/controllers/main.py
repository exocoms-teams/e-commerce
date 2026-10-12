import logging

from odoo import http
from odoo.http import request


_logger = logging.getLogger(__name__)


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

    @http.route(['/contact', '/contactus'], type='http', auth='public', website=True, sitemap=True)
    def contact(self, **kw):
        return request.render('monetique_theme.page_contact', {})

    def _create_opportunity(self, values, source):
        """Create an opportunity from a website form submission."""
        contact_name = values.get('name') or values.get('contact_name')
        subject = values.get('subject') or '%s - %s' % (
            source, contact_name or 'Site web'
        )
        description = values.get('message') or values.get('description') or values.get('details')

        return request.env['crm.lead'].sudo().create({
            'name': subject,
            'type': 'opportunity',
            'contact_name': contact_name,
            'email_from': values.get('email') or values.get('email_from'),
            'phone': values.get('phone') or values.get('mobile'),
            'description': description,
        })

    def _send_form_notifications(self, lead):
        """Send form emails without compromising the CRM lead creation."""
        template_ids = (
            'monetique_theme.email_template_lead_internal',
            'monetique_theme.email_template_lead_customer',
        )
        for template_id in template_ids:
            try:
                template = request.env.ref(template_id)
                template.sudo().send_mail(lead.id, force_send=True)
            except Exception as error:
                _logger.error(
                    'Unable to send notification %s for CRM lead %s: %s',
                    template_id, lead.id, error, exc_info=True,
                )

    @http.route('/contact/submit', type='http', auth='public', methods=['POST'], website=True, csrf=True)
    def contact_submit(self, **post):
        contact_name = post.get('name') or 'Site web'
        subject = post.get('subject') or contact_name
        description = (
            'Société : %s\n\n'
            'Message :\n%s'
        ) % (
            post.get('company') or 'Non renseignée',
            post.get('message') or 'Aucun message',
        )

        lead = request.env['crm.lead'].sudo().create({
            'name': 'Prise de contact - %s' % subject,
            'type': 'opportunity',
            'contact_name': post.get('name'),
            'email_from': post.get('email'),
            'phone': post.get('phone'),
            'partner_name': post.get('company'),
            'description': description,
        })
        self._send_form_notifications(lead)
        return request.redirect('/contact?submitted=1')

    @http.route('/audit/request', type='http', auth='public', methods=['POST'], website=True, csrf=True)
    def audit_request(self, **post):
        lead = self._create_opportunity(post, "Demande d'audit")
        self._send_form_notifications(lead)
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

        lead = request.env['crm.lead'].sudo().create({
            'name': 'Demande de devis - %s' % (post.get('name') or 'Site web'),
            'type': 'opportunity',
            'contact_name': post.get('name'),
            'email_from': post.get('email'),
            'phone': post.get('phone'),
            'partner_name': post.get('company'),
            'description': description,
        })
        self._send_form_notifications(lead)
        return request.redirect('/devis?submitted=1')
