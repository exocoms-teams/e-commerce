# -*- coding: utf-8 -*-
from odoo.addons.website_sale.controllers.main import WebsiteSale
from odoo.fields import Domain


class CapsuleHouseShopSearch(WebsiteSale):
    """Étend la recherche boutique pour inclure la surface (m²) des
    produits, en plus du nom/description déjà couverts nativement.

    Corrige CH-125 : jusqu'ici, chercher une taille (ex: '26', '30')
    dans la barre de recherche ne retournait aucun résultat pertinent
    (recherche native limitée au nom/description/code produit), donnant
    l'impression que la recherche "par taille" promise par le
    placeholder ("Chercher un modèle, une taille...") ne fonctionnait
    pas — confirmé en testant '26' qui retournait un produit de démo
    sans rapport ("Office Chair Black").

    Utilise le hook officiel _add_search_subdomains_hook() (voir
    website_sale/controllers/main.py, méthode _get_shop_domain) plutôt
    que de surcharger shop() entièrement : ce hook est prévu par Odoo
    pour ajouter des critères de recherche OR supplémentaires, sans
    risque de casser le reste de la logique native (pagination,
    filtres prix, tags...) à chaque montée de version d'Odoo.
    """

    def _add_search_subdomains_hook(self, search):
        return Domain('attribute_line_ids.value_ids.name', 'ilike', search)