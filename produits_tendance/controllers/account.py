# -*- coding: utf-8 -*-
from odoo import http
from odoo.http import request

class AccountController(http.Controller):

    def _get_account_menu(self, active_key):
        routes = [
            ('profil', 'Profil', '/compte/profil'),
            ('parametres', 'Paramètres', '/compte/parametres'),
            ('notifications', 'Notifications', '/compte/notifications'),
            ('facturation', 'Facturation', '/compte/facturation'),
            ('equipe', 'Équipe', '/compte/equipe'),
            ('api', 'API', '/compte/api'),
            ('export', 'Export', '/compte/export'),
            ('aide', 'Aide & Support', '/compte/aide'),
        ]
        return [
            {
                'key': k,
                'label': label,
                'url': url,
                'active': (k == active_key)
            }
            for k, label, url in routes
        ]

    @http.route(['/compte/profil'], type='http', auth='user', website=True, methods=['GET', 'POST'])
    def account_profile(self, **post):
        user = request.env.user
        values = {
            'user': user,
            'menu': self._get_account_menu('profil'),
            'page_title': 'Profil',
            'success': False,
            'error': False,
        }
        if request.httprequest.method == 'POST':
            name = post.get('name')
            if name:
                user.sudo().write({'name': name})
                values['success'] = True
            else:
                values['error'] = "Le nom ne peut pas être vide."
                
        return request.render('produits_tendance.account_profil_page', values)

    @http.route([
        '/compte/parametres',
        '/compte/notifications',
        '/compte/facturation',
        '/compte/equipe',
        '/compte/api',
        '/compte/export',
        '/compte/aide'
    ], type='http', auth='user', website=True)
    def account_coming_soon(self, **kw):
        path = request.httprequest.path.split('/')[-1]
        labels = {
            'parametres': 'Paramètres',
            'notifications': 'Notifications',
            'facturation': 'Facturation',
            'equipe': 'Équipe',
            'api': 'API',
            'export': 'Export',
            'aide': 'Aide & Support'
        }
        values = {
            'menu': self._get_account_menu(path),
            'page_title': labels.get(path, 'Espace Compte'),
        }
        return request.render('produits_tendance.account_coming_soon_page', values)