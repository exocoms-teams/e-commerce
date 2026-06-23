from odoo import http
from odoo.http import request
import json

class ExtensionController(http.Controller):

    @http.route('/extension-dashboard', type='http', auth='public', website=True)
    def dashboard_page(self):
        return request.render('your_module_name.extension_dashboard_page')

    @http.route('/extension/api/stats', type='json', auth='public', methods=['POST'])
    def get_stats(self):
        tracking_model = request.env['extension.tracking']
        stats = tracking_model.get_dashboard_stats()
        return stats

    @http.route('/extension/api/tracking-data', type='json', auth='public', methods=['POST'])
    def get_tracking_data(self):
        tracking_model = request.env['extension.tracking']
        records = tracking_model.search([], limit=50)
        
        data = []
        for record in records:
            data.append({
                'product_name': record.product_name,
                'website': dict(record._fields['website'].selection).get(record.website, ''),
                'price': record.price,
                'trend_score': record.trend_score,
                'create_date': record.create_date.strftime('%Y-%m-%d %H:%M'),
            })
        return data