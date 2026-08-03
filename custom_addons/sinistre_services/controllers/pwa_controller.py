# -*- coding: utf-8 -*-
"""
pwa_controller.py — Routes PWA + Service Worker Firebase dynamique
"""
import os

from odoo import http
from odoo.http import request, Response
from odoo.modules.module import get_module_path

from .firebase_utils import firebase_params, inject_firebase_sw


class PWAController(http.Controller):

    @http.route('/pwa/', type='http', auth='public', website=False)
    def pwa_index(self, **kwargs):
        return request.redirect('/sinistre_services/static/pwa/index.html')

    @http.route('/pwa/<path:path>', type='http', auth='public', website=False)
    def pwa_static(self, path, **kwargs):
        if path == 'sw.js':
            return self.pwa_sw_js()
        return request.redirect(f'/sinistre_services/static/pwa/{path}')

    @http.route('/sinistre_services/static/pwa/sw.js', type='http', auth='public', csrf=False)
    def pwa_sw_js(self):
        """Service Worker avec clés Firebase injectées depuis les paramètres Odoo."""
        mod_path = get_module_path('sinistre_services')
        sw_path = os.path.join(mod_path, 'static', 'pwa', 'sw.js')
        try:
            with open(sw_path, 'r', encoding='utf-8') as handle:
                content = handle.read()
        except OSError:
            return Response('// sw.js introuvable', status=404, content_type='application/javascript')

        params = firebase_params(request.env)
        content = inject_firebase_sw(content, params)
        return Response(
            content,
            content_type='application/javascript; charset=utf-8',
            headers={'Cache-Control': 'no-cache, no-store, must-revalidate'},
        )
