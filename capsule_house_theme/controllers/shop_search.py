# -*- coding: utf-8 -*-
import re

from odoo.addons.website_sale.controllers.main import WebsiteSale
from odoo.fields import Domain


class CapsuleHouseShopSearch(WebsiteSale):
    """Étend la recherche boutique pour inclure la surface (m²) des
    produits, en plus du nom/description déjà couverts nativement.

    Corrige CH-125 : chercher une taille (ex: '26', '20 m²') dans la
    barre de recherche ne retournait aucun résultat pertinent (recherche
    native limitée au nom/description/code produit).

    Utilise le hook officiel _add_search_subdomains_hook() prévu par
    Odoo pour ajouter des critères OR supplémentaires sans surcharger
    shop() entièrement.

    Garde-fou : le critère surface n'est ajouté que si le terme contient
    un chiffre — évite d'élargir les recherches purement textuelles
    ('Studio', 'Cabine') avec un match parasite sur les noms de valeurs
    d'attributs.
    """

    def _add_search_subdomains_hook(self, search):
        term = (search or '').strip()
        if not re.search(r'\d', term):
            return None
        return Domain('attribute_line_ids.value_ids.name', 'ilike', term)