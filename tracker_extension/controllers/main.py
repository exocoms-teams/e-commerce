from odoo import http
from odoo.http import request


class ExtensionController(http.Controller):

    @http.route('/extension-dashboard', type='http', auth='public', website=True)
    def dashboard_page(self):
        return request.render('tracker_extension.extension_dashboard_page')

    # Changed from 'json' to 'jsonrpc' for Odoo 19
    @http.route('/extension/api/stats', type='jsonrpc', auth='public', methods=['POST'])
    def get_stats(self):
        tracking_model = request.env['extension.tracking']
        stats = tracking_model.get_dashboard_stats()
        return stats

    # Changed from 'json' to 'jsonrpc' for Odoo 19
    @http.route('/extension/api/tracking-data', type='jsonrpc', auth='public', methods=['POST'])
    def get_tracking_data(self):
        tracking_model = request.env['extension.tracking']
        records = tracking_model.search([], limit=50)
        
        data = []
        for record in records:
            website_selection = dict(record._fields['website'].selection)
            data.append({
                'product_name': record.product_name,
                'website': website_selection.get(record.website, ''),
                'price': record.price,
                'trend_score': record.trend_score,
                'create_date': record.create_date.strftime('%Y-%m-%d %H:%M'),
            })
        return data