# -*- coding: utf-8 -*-
import re

from odoo.http import request
from odoo.addons.website_sale.controllers.main import WebsiteSale
from odoo.fields import Domain

NUMBER_RE = re.compile(r'\d+(?:[.,]\d+)?')
UNIT_ONLY_RE = re.compile(r'^(m²|m2|sqm|m)$', re.IGNORECASE)


def _numbers(text):
    return [float(n.replace(',', '.')) for n in NUMBER_RE.findall(text or '')]


class CapsuleHouseShopSearch(WebsiteSale):
    """CH-125 : la recherche boutique comprend les surfaces (m²).

    Les surfaces sont stockées comme des plages de texte ("15-20 m²",
    "20-30 m²"...) dans la valeur d'attribut "Surface". Chercher "26"
    doit donc trouver les produits proposant une plage qui contient 26,
    et "18-25" ceux dont une plage chevauche 18-25.

    Le hook natif est appelé mot par mot : un mot qui n'est qu'une unité
    ("m²", "m2", "sqm") est neutralisé pour que "20 m²" fonctionne
    comme "20".
    """

    def _add_search_subdomains_hook(self, search):
        term = (search or '').strip()
        if UNIT_ONLY_RE.match(term):
            return Domain('id', '>', 0)

        wanted = _numbers(term)
        if not wanted:
            return None
        low_w, high_w = min(wanted), max(wanted)

        values = request.env['product.attribute.value'].sudo().search([
            ('attribute_id.name', 'ilike', 'surface'),
        ])
        matching_ids = []
        for value in values:
            bounds = _numbers(value.name)
            if not bounds:
                continue
            if min(bounds) <= high_w and max(bounds) >= low_w:
                matching_ids.append(value.id)

        return Domain('attribute_line_ids.value_ids', 'in', matching_ids)