# -*- coding: utf-8 -*-
"""
pwa_controller.py — Sert les fichiers statiques de la PWA depuis Odoo
Route : /pwa/*

Permet d'héberger la PWA directement dans Odoo SH sans serveur séparé.
Pour Odoo SH, mettre les fichiers PWA dans :
  sinistre_services/static/pwa/

Et ils seront servis à :
  https://votre-instance.odoo.com/sinistre_services/static/pwa/index.html

Ou configurer un redirect /pwa/ → /sinistre_services/static/pwa/
"""
from odoo import http
from odoo.http import request


class PWAController(http.Controller):

    @http.route('/pwa/', type='http', auth='public', website=False)
    def pwa_index(self, **kwargs):
        """Redirige vers l'index de la PWA dans les assets statiques."""
        return request.redirect('/sinistre_services/static/pwa/index.html')

    @http.route('/pwa/<path:path>', type='http', auth='public', website=False)
    def pwa_static(self, path, **kwargs):
        """Redirige les fichiers PWA vers les assets statiques du module."""
        return request.redirect(f'/sinistre_services/static/pwa/{path}')
