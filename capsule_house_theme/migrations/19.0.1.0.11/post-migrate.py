# -*- coding: utf-8 -*-
"""
Rejoue run_theme_maintenance() après une mise à jour du module vers la
version 19.0.1.0.11.

Correctif purement XML/CSS (shop.xml + odoo-integration.css), en réponse
à la demande client de gérer la boutique de façon "native Odoo" comme
sur exocoms_theme :

- shop.xml : ajout d'un xpath explicite `hasLeftColumn=True` sur
  website_sale.products (même technique que boutique_sidebar dans
  exocoms_theme). À la différence d'exocoms (qui masque ensuite sa
  sidebar native au profit d'un méga-menu catégories statique custom),
  ici la sidebar native reste VISIBLE : c'est elle qui porte le filtre
  "Surface (m²)" attaché via _attach_shop_filters_to_products() (déjà
  en place depuis la 19.0.1.0.x précédente).
- odoo-integration.css : nouvelle section stylant
  .o_wsale_products_categories et .o_wsale_products_attributes avec nos
  variables --ch-*, jusqu'ici non habillées (seuls l'en-tête de grille,
  le filtre prix et le tri l'étaient).

Aucun changement de logique Python : ce correctif s'applique
automatiquement au rechargement des vues/assets. Rejeu de
run_theme_maintenance() ici uniquement par cohérence avec la convention
du module (un dossier de migration par bump de version).
"""
import logging

from odoo import api, SUPERUSER_ID

_logger = logging.getLogger(__name__)


def migrate(cr, version):
    from odoo.addons.capsule_house_theme import run_theme_maintenance

    env = api.Environment(cr, SUPERUSER_ID, {})
    _logger.info(
        "capsule_house_theme: post-migrate 19.0.1.0.11 — rejeu de "
        "run_theme_maintenance() (sidebar boutique native visible + "
        "filtre Surface m² stylé)."
    )
    run_theme_maintenance(env)
