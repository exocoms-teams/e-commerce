from odoo import http
from odoo.http import request
import logging

_logger = logging.getLogger(__name__)


class OaBeautyHomepage(http.Controller):
    """
    Override the default Odoo homepage route.

    Odoo's website module defines its own '/' handler in
    odoo/addons/website/controllers/main.py (class Website, method index).
    By declaring the same route in a dependent module, our handler takes
    precedence because Odoo picks the last-registered route for a given
    URL+method combination, and addons load after core modules.
    """

    @http.route('/', type='http', auth='public', website=True)
    def homepage(self, **kw):
        # Fetch up to 3 published products for the shop preview section.
        try:
            products = request.env['product.template'].sudo().search(
                [('is_published', '=', True), ('sale_ok', '=', True)],
                order='website_sequence asc, id asc',
                limit=3,
            )
        except Exception:
            products = request.env['product.template'].sudo().browse()

        return request.render(
            'oa_beauty_theme.view_homepage_lumiere',
            {'hp_products': products},
        )


class OaBeautyContact(http.Controller):

    @http.route(
        '/oa-beauty/contact/submit',
        type='http',
        auth='public',
        methods=['POST'],
        website=True,
        csrf=True,
    )
    def contact_submit(
        self,
        from_name='',
        email='',
        phone='',
        subject='',
        message='',
        **kwargs,
    ):
        if not from_name.strip() or not email.strip() or not message.strip():
            return request.redirect('/?contact_error=1')

        try:
            company = request.website.company_id
            to_email = company.email or 'contact@oabeauty.example'

            body_html = (
                '<p><strong>Name:</strong> {name}</p>'
                '<p><strong>Email:</strong> {email}</p>'
                '<p><strong>Phone:</strong> {phone}</p>'
                '<p><strong>Subject:</strong> {subject}</p>'
                '<hr/>'
                '<p>{message}</p>'
            ).format(
                name=from_name,
                email=email,
                phone=phone or '-',
                subject=subject or '-',
                message=message.replace('\n', '<br/>'),
            )

            mail = request.env['mail.mail'].sudo().create({
                'subject': '[O&A Beauty] Contact - %s' % (subject or 'Website Enquiry'),
                'body_html': body_html,
                'email_from': '%s <%s>' % (from_name, email),
                'email_to': to_email,
            })
            mail.sudo().send()

        except Exception:
            _logger.exception('O&A Beauty contact form failed to send mail')
            return request.redirect('/?contact_error=1')

        return request.redirect('/?contact_sent=1')
