from odoo import http
from odoo.http import request
import logging

_logger = logging.getLogger(__name__)


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
                '<p><strong>Name:</strong> ' + from_name + '</p>'
                '<p><strong>Email:</strong> ' + email + '</p>'
                '<p><strong>Phone:</strong> ' + (phone or '-') + '</p>'
                '<p><strong>Subject:</strong> ' + (subject or '-') + '</p>'
                '<hr/>'
                '<p>' + message.replace('\n', '<br/>') + '</p>'
            )

            mail = request.env['mail.mail'].sudo().create({
                'subject': '[O&A Beauty] ' + (subject or 'Website Enquiry'),
                'body_html': body_html,
                'email_from': from_name + ' <' + email + '>',
                'email_to': to_email,
            })
            mail.sudo().send()

        except Exception:
            _logger.exception('OaBeauty contact form error')
            return request.redirect('/?contact_error=1')

        return request.redirect('/?contact_sent=1')
