from odoo import http
from odoo.http import request

class SerruproController(http.Controller):

    @http.route('/serrupro', auth='public', website=True, type='http')
    def index(self, **kw):
        return request.render('serrupro.homepage')

    @http.route('/serrupro/faq', auth='public', website=True, type='http')
    def faq_page(self, **kw):
        questions = request.env['serrupro.faq.question'].sudo().search([('published', '=', True)], order='id desc')
        return request.render('serrupro.faq_page', {
            'faq_questions': questions,
            'form_data': kw,
            'error': kw.get('error', False),
            'success': kw.get('success', False),
        })

    @http.route('/serrupro/faq/ask', auth='public', website=True, type='http', methods=['POST'], csrf=True)
    def faq_ask(self, **post):
        name = post.get('name', '').strip()
        email = post.get('email', '').strip()
        question_text = post.get('question', '').strip()

        if not (name and email and question_text):
            post['error'] = True
            return request.redirect('/serrupro/faq?error=1')

        request.env['serrupro.faq.question'].sudo().create({
            'name': question_text,
            'answer': False,
            'contact_email': email,
            'published': False,
            'state': 'new',
        })
        return request.redirect('/serrupro/faq?success=1')