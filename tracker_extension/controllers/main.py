from odoo import http
from odoo.http import request

class ExtensionController(http.Controller):

    @http.route('/', type='http', auth='public', website=True)
    def home_page(self):
        return request.render('tracker_extension.website_homepage')

    @http.route('/tracker-extension', type='http', auth='public', website=True)
    def download_page(self):
        return request.render('tracker_extension.extension_download_page')

    @http.route('/extension-dashboard', type='http', auth='public', website=True)
    def dashboard_page(self):
        return request.render('tracker_extension.extension_dashboard_page')