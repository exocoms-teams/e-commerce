from odoo import http
from odoo.http import request
import json
import re


class TrendIngestController(http.Controller):

    @http.route('/api/trend/ingest', type='http', auth='none', methods=['POST'], csrf=False)
    def ingest(self, **kwargs):
        try:
            data = json.loads(request.httprequest.data)
        except Exception:
            return self._json_response({'status': 'error', 'code': 'invalid_json'}, 400)

        api_key = data.get('api_key')
        if not api_key:
            return self._json_response(
                {'status': 'error', 'code': 'missing_field', 'field': 'api_key'}, 401
            )
        if not self.check_api_key(api_key):
            return self._json_response(
                {'status': 'error', 'code': 'invalid_api_key'}, 403
            )

        data_type = data.get('type')
        if not data_type:
            return self._json_response(
                {'status': 'error', 'code': 'missing_field', 'field': 'type'}, 400
            )

        payload = data.get('data', {})
        return self.route_by_type(data_type, payload)

    def route_by_type(self, type, data):
        if type == 'product':
            return self._handle_product(data)
        elif type == 'ad':
            return self._handle_ad(data)
        elif type == 'score':
            return self._handle_score(data)
        else:
            return self._json_response(
                {'status': 'error', 'code': 'unknown_type',
                 'field': 'type', 'received': type}, 400
            )

    def _validate_payload(self, payload):
        # Vérification format date (si présente)
        if payload.get('date'):
            if not re.match(r'^\d{4}-\d{2}-\d{2}$', payload['date']):
                return self._json_response(
                    {'status': 'error', 'code': 'invalid_format',
                     'field': 'date', 'expected': 'YYYY-MM-DD'}, 400
                )

        # Vérification format country (si présent)
        if payload.get('country'):
            country = payload['country']
            if len(country) != 2 or not country.isupper():
                return self._json_response(
                    {'status': 'error', 'code': 'invalid_format',
                     'field': 'country',
                     'expected': 'ISO 3166-1 alpha-2 (ex: MA, FR)'}, 400
                )

        return None  # None = pas d'erreur

    def _handle_product(self, payload):
        required_fields = ['name', 'product_ref', 'category', 'country', 'source']
        for field in required_fields:
            if not payload.get(field):
                return self._json_response(
                    {'status': 'error', 'code': 'missing_field', 'field': field}, 400
                )

        error = self._validate_payload(payload)
        if error:
            return error

        env = request.env(su=True)

        category = env['trend.category'].search(
            [('name', '=', payload['category'])], limit=1
        )
        if not category:
            category = env['trend.category'].create({'name': payload['category']})

        existing = env['trend.product'].search([
            ('product_ref', '=', payload['product_ref']),
            ('source', '=', payload['source']),
        ], limit=1)

        vals = {
            'name': payload['name'],
            'product_ref': payload['product_ref'],
            'category_id': category.id,
            'sales_count': payload.get('sales_count', 0),
            'date': payload.get('date'),
            'score_site_x': payload.get('score_site_x'),
            'country': payload['country'],
            'source': payload['source'],
        }
        vals = {k: v for k, v in vals.items() if v is not None}

        if existing:
            existing.write(vals)
            record = existing
        else:
            record = env['trend.product'].create(vals)

        return self._json_response(
            {'status': 'success', 'type': 'product', 'id': record.id}, 200
        )

    def _handle_ad(self, payload):
        required_fields = ['ad_ref', 'product_ref', 'country', 'social_network']
        for field in required_fields:
            if not payload.get(field):
                return self._json_response(
                    {'status': 'error', 'code': 'missing_field', 'field': field}, 400
                )

        error = self._validate_payload(payload)
        if error:
            return error

        env = request.env(su=True)

        existing = env['trend.ad'].search(
            [('ad_ref', '=', payload['ad_ref'])], limit=1
        )

        vals = {
            'ad_ref': payload['ad_ref'],
            'product_ref': payload['product_ref'],
            'country': payload['country'],
            'social_network': payload['social_network'],
            'likes_count': payload.get('likes_count', 0),
            'shares_count': payload.get('shares_count', 0),
        }

        if existing:
            existing.write(vals)
            record = existing
        else:
            record = env['trend.ad'].create(vals)

        return self._json_response(
            {'status': 'success', 'type': 'ad', 'id': record.id}, 200
        )

    def _handle_score(self, payload):
        required_fields = ['product_ref', 'computed_score']
        for field in required_fields:
            if not payload.get(field):
                return self._json_response(
                    {'status': 'error', 'code': 'missing_field', 'field': field}, 400
                )

        env = request.env(su=True)

        product = env['trend.product'].search(
            [('product_ref', '=', payload['product_ref'])], limit=1
        )
        if not product:
            return self._json_response(
                {'status': 'error', 'code': 'product_not_found',
                 'product_ref': payload['product_ref']}, 404
            )

        vals = {
            'product_id': product.id,
            'computed_score': payload['computed_score'],
        }
        if payload.get('computed_at'):
            vals['computed_at'] = payload['computed_at']

        record = env['trend.score'].create(vals)

        return self._json_response(
            {'status': 'success', 'type': 'score', 'id': record.id}, 200
        )

    def check_api_key(self, key):
        valid_key = request.env['ir.config_parameter'].sudo().get_param('winners.api_key')
        return valid_key and key == valid_key

    def _json_response(self, payload, status):
        return request.make_response(
            json.dumps(payload),
            status=status,
            headers=[('Content-Type', 'application/json')]
        )