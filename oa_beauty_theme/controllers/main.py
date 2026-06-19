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
        """
        Handles the contact form on the homepage.
        Replaces the original EmailJS integration with a proper server-side
        mail send via Odoo's mail.mail model (requires 'mail' in depends).
        On success  → redirect to /?contact_sent=1
        On failure  → redirect to /?contact_error=1
        """
        # Basic server-side validation
        if not from_name.strip() or not email.strip() or not message.strip():
            return request.redirect('/?contact_error=1')

        try:
            company = request.website.company_id
            to_email = company.email or 'contact@oabeauty.example'

            body_html = """
<p><strong>Name:</strong> {name}</p>
<p><strong>Email:</strong> {email}</p>
<p><strong>Phone:</strong> {phone}</p>
<p><strong>Subject:</strong> {subject}</p>
<hr/>
<p>{message}</p>
            """.format(
                name=from_name,
                email=email,
                phone=phone or '—',
                subject=subject or '—',
                message=message.replace('\n', '<br/>'),
            )

            mail = request.env['mail.mail'].sudo().create({
                'subject': '[O&A Beauty] Contact – %s' % (subject or 'Website Enquiry'),
                'body_html': body_html,
                'email_from': '%s <%s>' % (from_name, email),
                'email_to': to_email,
            })
            mail.sudo().send()

        except Exception:
            _logger.exception('O&A Beauty contact form failed to send mail')
            return request.redirect('/?contact_error=1')

        return request.redirect('/?contact_sent=1')
