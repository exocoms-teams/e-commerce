from odoo import http
from odoo.http import request


class TrendIngestController(http.Controller):

    @http.route('/api/trend/ingest', type='json', auth='none', methods=['POST'], csrf=False)
    def ingest(self, **kwargs):
        api_key = kwargs.get('api_key')

        if not api_key:
            return {
                'status': 'error',
                'code': 'missing_field',
                'field': 'api_key'
            }

        if not self._is_valid_api_key(api_key):
            return {
                'status': 'error',
                'code': 'invalid_api_key'
            }

        data_type = kwargs.get('type')
        if data_type not in ('product', 'score', 'ad'):
            return {
                'status': 'error',
                'code': 'missing_field',
                'field': 'type'
            }

        return {
            'status': 'success',
            'message': 'Authentification reussie'
        }

    def _is_valid_api_key(self, key):
        valid_key = request.env['ir.config_parameter'].sudo().get_param('trend.api_key')
        return valid_key and key == valid_key