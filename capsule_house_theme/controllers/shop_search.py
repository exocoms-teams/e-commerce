# -*- coding: utf-8 -*-
import re

from odoo.http import request
from odoo.addons.website_sale.controllers.main import WebsiteSale
from odoo.fields import Domain

from ..data_definition.__init__ import GAMMES_DATA

NUMBER_RE = re.compile(r'\d+(?:[.,]\d+)?')
UNIT_ONLY_RE = re.compile(r'^(m²|m2|sqm|m)$', re.IGNORECASE)


def _numbers(text):
    return [float(n.replace(',', '.')) for n in NUMBER_RE.findall(text or '')]


class CapsuleHouseShopSearch(WebsiteSale):
    """CH-125 : la recherche boutique comprend les tailles (m²).

    Option B (voir discussion CH-125) : faute d'avoir les vraies
    surfaces sur chaque produit (les 24 produits actuels ont tous les
    3 mêmes plages de démo, données pas encore fournies par le client),
    un nombre recherché est comparé aux VRAIS formats déclarés dans
    GAMMES_DATA (source unique, même donnée que /nos-gammes et
    l'accueil) pour déterminer quelle(s) gamme(s) le couvrent, puis la
    recherche est élargie à la catégorie boutique de cette/ces gamme(s)
    (même nom que la gamme, voir SHOP_CATEGORIES/_setup_shop_categories).
    À affiner en option A une fois le vrai catalogue fourni : remplacer
    ce hook par un filtre direct sur l'attribut Surface de chaque
    produit, sans passer par la catégorie.

    Le hook natif _add_search_subdomains_hook est appelé mot par mot
    (voir website_sale/controllers/main.py, _get_shop_domain) : un mot
    qui n'est qu'une unité ("m²", "m2", "sqm") est neutralisé pour que
    "20 m²" se comporte comme "20".
    """

    def _add_search_subdomains_hook(self, search):
        term = (search or '').strip()
        if UNIT_ONLY_RE.match(term):
            return Domain('id', '>', 0)

        wanted = _numbers(term)
        if not wanted:
            return None
        low_w, high_w = min(wanted), max(wanted)

        matching_names = []
        for gamme in GAMMES_DATA:
            for fmt in gamme.get('formats', []):
                bounds = _numbers(fmt.get('surface_fr', ''))
                if len(bounds) == 2 and min(bounds) <= high_w and max(bounds) >= low_w:
                    matching_names.append(gamme['name'])
                    break

        if not matching_names:
            return None

        categories = request.env['product.public.category'].sudo().search([
            ('name', 'in', matching_names),
            ('parent_id', '=', False),
        ])
        if not categories:
            return None

        return Domain('public_categ_ids', 'child_of', categories.ids)