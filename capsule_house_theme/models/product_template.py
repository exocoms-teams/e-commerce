# -*- coding: utf-8 -*-
import re

from odoo import api, models
from odoo.fields import Domain

from ..data_definition.__init__ import GAMMES_DATA

NUMBER_RE = re.compile(r'\d+(?:[.,]\d+)?')
UNIT_ONLY_RE = re.compile(r'^(m²|m2|sqm|m)$', re.IGNORECASE)


def _numbers(text):
    return [float(n.replace(',', '.')) for n in NUMBER_RE.findall(text or '')]


def _gammes_matching(term):
    """Renvoie les noms de gammes (Capsule, Cabine...) dont au moins un
    format déclaré dans GAMMES_DATA couvre le nombre cherché."""
    wanted = _numbers(term)
    if not wanted:
        return []
    low_w, high_w = min(wanted), max(wanted)
    names = []
    for gamme in GAMMES_DATA:
        for fmt in gamme.get('formats', []):
            bounds = _numbers(fmt.get('surface_fr', ''))
            if len(bounds) == 2 and min(bounds) <= high_w and max(bounds) >= low_w:
                names.append(gamme['name'])
                break
    return names


class ProductTemplate(models.Model):
    _inherit = 'product.template'

    @api.model
    def _search_get_detail(self, website, order, options):
        """CH-125 : la recherche boutique (barre de recherche /shop)
        comprend les tailles (m²).

        _search_get_detail() alimente website._search_with_fuzzy(), qui
        fournit la VRAIE liste de produits affichée sur /shop (voir
        website_sale/controllers/main.py, _shop_lookup_products puis
        `products = search_product[offset:offset + ppg]`) — contrairement
        au hook _add_search_subdomains_hook (controllers/shop_search.py),
        qui n'influence que le comptage et les tags de catégorie affichés,
        jamais la liste réelle. D'où ce deuxième point d'entrée, sur le
        modèle plutôt que sur le contrôleur.

        Option B (voir discussion CH-125) : faute d'avoir les vraies
        surfaces par produit (catalogue pas encore fourni, tous les
        produits actuels partagent les 3 mêmes plages de démo), un
        nombre recherché est élargi à la catégorie boutique des gammes
        dont un format (GAMMES_DATA) couvre ce nombre. À remplacer par
        un filtre direct sur l'attribut Surface du produit une fois le
        vrai catalogue disponible (option A).
        """
        result = super()._search_get_detail(website, order, options)

        def _extra(env, term):
            term = (term or '').strip()
            if UNIT_ONLY_RE.match(term):
                return Domain('id', '>', 0)

            names = _gammes_matching(term)
            if not names:
                return Domain('id', '=', 0)

            categories = env['product.public.category'].sudo().search([
                ('name', 'in', names),
                ('parent_id', '=', False),
            ])
            if not categories:
                return Domain('id', '=', 0)

            return Domain('public_categ_ids', 'child_of', categories.ids)

        result['search_extra'] = _extra
        return result
