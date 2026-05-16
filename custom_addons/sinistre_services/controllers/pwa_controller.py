# -*- coding: utf-8 -*-
"""
pwa_controller.py — Route /pwa/ vers les assets statiques PWA
"""
from odoo import http
from odoo.http import request


class PWAController(http.Controller):

    @http.route('/pwa/', type='http', auth='public', website=False)
    def pwa_index(self, **kwargs):
        return request.redirect('/sinistre_services/static/pwa/index.html')

    @http.route('/pwa/<path:path>', type='http', auth='public', website=False)
    def pwa_static(self, path, **kwargs):
        return request.redirect(f'/sinistre_services/static/pwa/{path}')
