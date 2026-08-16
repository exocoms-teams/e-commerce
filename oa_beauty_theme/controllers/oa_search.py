from odoo import http
from odoo.http import request


class OASearchController(http.Controller):

    def _session_key(self):
        return getattr(request.session, 'sid', False) or request.session.get('session_token')

    def _log_event(self, query, payload, event_type='search'):
        normalized = request.env['oa.search.service'].sudo().normalize_query(query)
        request.env['oa.search.log'].sudo().create({
            'query': (query or '')[:120],
            'normalized_query': normalized,
            'result_count': int(payload.get('count', 0) or 0),
            'is_zero_result': not bool(payload.get('count')),
            'event_type': event_type,
            'website_id': request.website.id if request.website else False,
            'session_id': self._session_key(),
        })

    @http.route('/api/oa/search', type='jsonrpc', auth='public', website=True, csrf=False, methods=['POST'])
    def search(self, query=None, limit=8, **kwargs):
        query = (query or kwargs.get('q') or '').strip()[:120]
        try:
            limit = min(max(int(limit or 8), 1), 12)
        except (TypeError, ValueError):
            limit = 8

        if len(query) < 2:
            payload = {'query': query, 'results': [], 'suggestions': [], 'count': 0}
            return payload

        payload = request.env['oa.search.service'].sudo().search_products(
            query,
            limit=limit,
            website=request.website,
        )
        self._log_event(query, payload, event_type='autocomplete')
        return payload

    @http.route('/api/oa/search/click', type='jsonrpc', auth='public', website=True, csrf=False, methods=['POST'])
    def click(self, query=None, product_id=None, category_id=None, event_type='product_click', **kwargs):
        vals = {
            'query': (query or '')[:120],
            'normalized_query': request.env['oa.search.service'].sudo().normalize_query(query),
            'event_type': event_type if event_type in ('product_click', 'category_click') else 'product_click',
            'website_id': request.website.id if request.website else False,
            'session_id': self._session_key(),
        }
        if product_id:
            try:
                product = request.env['product.template'].sudo().browse(int(product_id)).exists()
            except (TypeError, ValueError):
                product = request.env['product.template']
            if product and product.is_published:
                vals['product_id'] = product.id
        if category_id:
            try:
                category = request.env['product.public.category'].sudo().browse(int(category_id)).exists()
            except (TypeError, ValueError):
                category = request.env['product.public.category']
            if category:
                vals['category_id'] = category.id
        request.env['oa.search.log'].sudo().create(vals)
        return {'ok': True}
