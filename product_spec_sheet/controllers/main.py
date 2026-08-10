from odoo import http
from odoo.http import request


class ProductSpecCompareController(http.Controller):

    def _resolve_products(self, product_ids='', add=None, remove=None):
        """Parse la chaîne d'ids, applique add/remove, renvoie un recordset publié."""
        ids = []
        for chunk in (product_ids or '').split(','):
            chunk = chunk.strip()
            if chunk.isdigit():
                ids.append(int(chunk))
        if add and str(add).isdigit() and int(add) not in ids:
            ids.append(int(add))
        if remove and str(remove).isdigit() and int(remove) in ids:
            ids.remove(int(remove))
        Product = request.env['product.template'].sudo()
        return Product.browse(ids).exists().filtered(lambda p: p.website_published)

    def _compare_context(self, products):
        """Construit le dict de contexte commun pour la page de comparaison."""
        categories = products.mapped('spec_line_ids.category_id').sorted(
            key=lambda c: (c.sequence, c.name or '')
        )
        category_attributes = {}
        for category in categories:
            attrs = products.mapped('spec_line_ids').filtered(
                lambda l: l.category_id == category
            ).mapped('attribute_id').sorted(key=lambda a: (a.sequence, a.name or ''))
            category_attributes[category.id] = attrs

        domain = [('website_published', '=', True), ('sale_ok', '=', True)]
        if products:
            domain.append(('id', 'not in', products.ids))
        available_products = request.env['product.template'].sudo().search(
            domain, limit=200, order='name'
        )
        remove_ids_map = {
            p.id: ','.join(str(o.id) for o in products if o.id != p.id)
            for p in products
        }
        return {
            'products': products,
            'categories': categories,
            'category_attributes': category_attributes,
            'available_products': available_products,
            'product_ids_str': ','.join(str(p.id) for p in products),
            'remove_ids_map': remove_ids_map,
        }

    @http.route(['/product-specs/compare'], type='http', auth='public', website=True, sitemap=False)
    def compare(self, product_ids='', add=None, remove=None, **kw):
        """Page de comparaison interactive sur le site."""
        products = self._resolve_products(product_ids, add, remove)
        return request.render(
            'product_spec_sheet.product_spec_compare_page',
            self._compare_context(products),
        )

    @http.route(['/product-specs/compare/print'], type='http', auth='public', website=True, sitemap=False)
    def compare_print(self, product_ids='', **kw):
        """
        Génère le PDF du comparatif directement depuis le site web.

        Le PDF est produit par le moteur de rapport Odoo (qweb-pdf) et renvoyé
        en téléchargement. Seuls les produits publiés sont inclus.

        Exemple d'URL :
            /product-specs/compare/print?product_ids=12,45,67
        """
        ids = [int(c.strip()) for c in (product_ids or '').split(',') if c.strip().isdigit()]
        products = request.env['product.template'].sudo().browse(ids).exists().filtered(
            lambda p: p.website_published
        )
        if not products:
            return request.not_found()

        pdf_content, _content_type = request.env['ir.actions.report'].sudo()._render_qweb_pdf(
            'product_spec_sheet.report_product_spec_compare',
            res_ids=products.ids,
        )

        filename = 'Comparatif_caracteristiques.pdf'
        return request.make_response(
            pdf_content,
            headers=[
                ('Content-Type', 'application/pdf'),
                ('Content-Disposition', f'attachment; filename="{filename}"'),
            ],
        )


class ProductSpecFilterController(http.Controller):
    """Filtrage de la boutique par caractéristique produit."""

    def _parse_spec_filters(self, kw):
        """
        Extrait les filtres du querystring.
        Format attendu : spec_<attribute_id>=valeur1,valeur2
        Retourne {attribute_id: [valeurs]}
        """
        filters = {}
        for key, val in kw.items():
            if not key.startswith("spec_"):
                continue
            raw_id = key[5:]
            if not raw_id.isdigit() or not val:
                continue
            values = [v.strip() for v in val.split(",") if v.strip()]
            if values:
                filters[int(raw_id)] = values
        return filters

    def _apply_spec_filters(self, products, filters):
        """Filtre un recordset de produits selon les caractéristiques choisies."""
        if not filters:
            return products
        for attr_id, wanted in filters.items():
            products = products.filtered(
                lambda p: any(
                    line.attribute_id.id == attr_id
                    and any(w.lower() in (line.value or "").lower() for w in wanted)
                    for line in p.spec_line_ids
                )
            )
        return products

    @http.route(["/shop/spec-filter"], type="http", auth="public",
                website=True, sitemap=False)
    def spec_filter(self, category=None, **kw):
        """Page boutique filtrée par caractéristiques."""
        Product = request.env["product.template"].sudo()

        domain = [("website_published", "=", True), ("sale_ok", "=", True)]
        if category and str(category).isdigit():
            domain.append(("public_categ_ids", "child_of", int(category)))

        products = Product.search(domain, limit=500, order="name")

        filters = self._parse_spec_filters(kw)
        filtered = self._apply_spec_filters(products, filters)

        # Caractéristiques marquées comme filtrables
        attributes = request.env["product.spec.attribute"].sudo().search(
            [("website_filter", "=", True)],
            order="filter_sequence, name",
        )

        facets = []
        for attr in attributes:
            values = attr.get_filter_values()
            if values:
                facets.append({
                    "attribute": attr,
                    "values":    values,
                    "selected":  filters.get(attr.id, []),
                })

        return request.render("product_spec_sheet.shop_spec_filter_page", {
            "products":    filtered,
            "facets":      facets,
            "filters":     filters,
            "total_count": len(products),
            "shown_count": len(filtered),
            "category":    category,
        })
