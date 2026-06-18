# -*- coding: utf-8 -*-
from odoo import http
from odoo.http import request


class OaBeautyHomepage(http.Controller):
    """
    Serves the custom LUMIÈRE homepage at '/' with live product data.

    This controller overrides the default Odoo website homepage.
    Odoo's routing system picks the controller whose module has the
    highest sequence (or was loaded last).  Since 'website' defines
    its own '/' handler, we use the same signature; Odoo will use this
    one because it is declared in an addon that depends on 'website'.

    If another custom theme or module also declares '/', add
    `sequence=XX` (lower = higher priority) inside @http.route.
    """

    @http.route('/', type='http', auth='public', website=True)
    def homepage(self, **kw):
        """Render the LUMIÈRE homepage with up to 8 live products."""
        domain = [
            ('sale_ok', '=', True),
            ('website_published', '=', True),
        ]
        try:
            products = request.env['product.template'].sudo().search(
                domain,
                order='website_sequence asc, name asc',
                limit=8,
            )
        except Exception:
            products = request.env['product.template'].sudo().browse()

        values = {
            'products': products,
        }
        return request.render('oa_beauty_theme.homepage_lumiere', values)
