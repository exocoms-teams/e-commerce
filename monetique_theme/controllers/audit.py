from odoo import http
from odoo.http import request

class AuditController(http.Controller):

    @http.route('/audit', type='http', auth='public', website=True)
    def audit_page(self, **kwargs):
        return request.render('monetique_theme.page_audit')

    @http.route('/audit/submit', type='http', auth='public', website=True, methods=['POST'], csrf=True)
    def audit_submit(self, **post):
        request.env['mail.mail'].sudo().create({
            'subject': f"Demande audit — {post.get('name', '')}",
            'email_from': 'noreply@monetiques.fr',
            'email_to': 'contact@monetiques.fr',
            'body_html': f"""
                <h2>Nouvelle demande d audit</h2>
                <p><b>Nom :</b> {post.get('name', '')}</p>
                <p><b>Email :</b> {post.get('email', '')}</p>
                <p><b>Telephone :</b> {post.get('phone', '')}</p>
                <p><b>Commerce :</b> {post.get('commerce_type', '')}</p>
                <p><b>Nb caisses :</b> {post.get('nb_caisses', '')}</p>
                <p><b>Volume mensuel :</b> {post.get('volume', '')}</p>
                <p><b>TPE actuel :</b> {post.get('tpe_actuel', '')}</p>
                <p><b>Message :</b> {post.get('message', '')}</p>
            """,
        }).send()
        return request.render('monetique_theme.page_audit_merci')
