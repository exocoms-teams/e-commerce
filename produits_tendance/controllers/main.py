from odoo import http
from odoo.http import request
import json


class TrendIngestController(http.Controller):

    @http.route('/api/trend/ingest', type='http', auth='none', methods=['POST'], csrf=False)
    def ingest(self, **kwargs):
        try:
            data = json.loads(request.httprequest.data)
        except Exception:
            return request.make_response(
                json.dumps({'status': 'error', 'code': 'invalid_json'}),
                status=400,
                headers=[('Content-Type', 'application/json')]
            )

        api_key = data.get('api_key')

        if not api_key:
            return request.make_response(
                json.dumps({'status': 'error', 'code': 'missing_field', 'field': 'api_key'}),
                status=401,
                headers=[('Content-Type', 'application/json')]
            )

        if not self._is_valid_api_key(api_key):
            return request.make_response(
                json.dumps({'status': 'error', 'code': 'invalid_api_key'}),
                status=403,
                headers=[('Content-Type', 'application/json')]
            )

        data_type = data.get('type')
        if data_type not in ('product', 'score', 'ad'):
            return request.make_response(
                json.dumps({'status': 'error', 'code': 'missing_field', 'field': 'type'}),
                status=400,
                headers=[('Content-Type', 'application/json')]
            )

        return request.make_response(
            json.dumps({'status': 'success', 'message': 'Authentification reussie'}),
            status=200,
            headers=[('Content-Type', 'application/json')]
        )

    def _is_valid_api_key(self, key):
        valid_key = request.env['ir.config_parameter'].sudo().get_param('trend.api_key')
        return valid_key and key == valid_key