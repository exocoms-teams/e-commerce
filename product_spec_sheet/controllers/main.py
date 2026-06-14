from odoo import http
from odoo.http import request


class ProductSpecCompareController(http.Controller):

    @http.route(['/product-specs/compare'], type='http', auth='public', website=True, sitemap=False)
    def compare(self, product_ids='', add=None, remove=None, **kw):
        ids = []
        for chunk in (product_ids or '').split(','):
            chunk = chunk.strip()
            if chunk.isdigit():
                ids.append(int(chunk))

        if add and add.isdigit() and int(add) not in ids:
            ids.append(int(add))
        if remove and remove.isdigit() and int(remove) in ids:
            ids.remove(int(remove))

        Product = request.env['product.template'].sudo()
        products = Product.browse(ids).exists().filtered(
            lambda p: p.website_published
        )

        categories = products.mapped('spec_line_ids.category_id')
        categories = categories.sorted(key=lambda c: (c.sequence, c.name or ''))

        category_attributes = {}
        for category in categories:
            attrs = products.mapped('spec_line_ids').filtered(
                lambda l: l.category_id == category
            ).mapped('attribute_id')
            category_attributes[category.id] = attrs.sorted(
                key=lambda a: (a.sequence, a.name or '')
            )

        domain = [('website_published', '=', True), ('sale_ok', '=', True)]
        if products:
            domain.append(('id', 'not in', products.ids))
        available_products = Product.search(domain, limit=200, order='name')

        remove_ids_map = {
            product.id: ','.join(str(p.id) for p in products if p.id != product.id)
            for product in products
        }

        return request.render('product_spec_sheet.product_spec_compare_page', {
            'products': products,
            'categories': categories,
            'category_attributes': category_attributes,
            'available_products': available_products,
            'product_ids_str': ','.join(str(p.id) for p in products),
            'remove_ids_map': remove_ids_map,
        })
