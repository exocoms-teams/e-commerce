# -*- coding: utf-8 -*-
"""
Rejoue run_theme_maintenance() après une mise à jour du module vers la
version 19.0.1.0.21.

Demande client : "change le product design et met le comme sur exocoms
theme en chips" — restyle des cartes produit de la grille /shop en
carte arrondie avec ombre douce + effet de soulèvement au survol,
inspiré d'exocoms_theme.

Classes confirmées en inspectant le DOM réel de /shop sur cette
instance Odoo 19 (pas de reprise à l'aveugle des classes d'exocoms —
leur propre règle `.o_product` ne correspond à RIEN sur cette version
d'Odoo, probablement écrite pour une version antérieure) :
- `.o_wsale_product_grid_wrapper` : la vraie carte (coins arrondis,
  ombre, hover).
- `.oe_product_image` / `.oe_product_image_img` : image (coins
  arrondis en haut, zoom léger au survol).
- `.o_wsale_products_item_title` : titre produit.
- `.o_add_wishlist` : bouton wishlist (cercle discret superposé).

Rejeu de run_theme_maintenance() ici uniquement par cohérence avec la
convention du module — correctif pur CSS, aucune donnée à migrer.
"""
import logging

from odoo import api, SUPERUSER_ID

_logger = logging.getLogger(__name__)


def migrate(cr, version):
    from odoo.addons.capsule_house_theme import run_theme_maintenance

    env = api.Environment(cr, SUPERUSER_ID, {})
    _logger.info(
        "capsule_house_theme: post-migrate 19.0.1.0.21 — cartes produit "
        "de /shop restylées en 'chip' (coins arrondis, ombre, hover), "
        "classes natives vérifiées en direct (o_wsale_product_grid_wrapper "
        "et non o_product comme chez exocoms_theme)."
    )
    run_theme_maintenance(env)
