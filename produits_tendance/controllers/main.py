from odoo import http
from odoo.http import request

class TrendSubmissionController(http.Controller):

    # 1. Route pour AFFICHER le formulaire (GET)
    @http.route('/submit-trend', type='http', auth='public', website=True)
    def submit_trend_form(self, **kwargs):
        return request.render('produits_tendance.template_submit_trend_form', {})

    # 2. Route pour TRAITER le formulaire (POST)
    @http.route('/submit-trend/process', type='http', auth='public', website=True, methods=['POST'], csrf=True)
    def submit_trend_process(self, **post):
        if post:
            # sudo() permet au visiteur non connecté de créer l'enregistrement sans bloquer sur les droits
            request.env['trend.submission'].sudo().create({
                'name': post.get('name'),
                'product_ref': post.get('product_ref'),
                'category': post.get('category'),
                'country': post.get('country'),
                'submission_reason': post.get('submission_reason'),
                'submitted_by': request.env.user.name if request.env.user.name != 'Public user' else 'Visiteur Anonyme',
            })
        # Redirection vers la page avec un message de succès
        return request.redirect('/submit-trend?success=1')