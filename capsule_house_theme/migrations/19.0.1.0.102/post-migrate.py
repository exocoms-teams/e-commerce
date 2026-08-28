# -*- coding: utf-8 -*-
"""
Rejoue run_theme_maintenance() après une mise à jour du module vers la
version 19.0.1.0.102.

RETOUR CLIENT : "mes produit qui s'affiche sur les meilleur n'ont pas
la même configuration que le carousel de exocoms". Vérification du vrai
code d'exocoms_theme (views/partials/dashbord.xml, section "MEILLEURES
VENTES") : chez eux, ce n'est pas une grille statique mais un vrai
carousel Bootstrap 5 natif (data-bs-ride="carousel"), jusqu'à 16
produits regroupés par lots de 4 slides, défilement automatique (5s),
flèches précédent/suivant — aucun JS custom, uniquement les attributs
data-bs-* natifs déjà fournis par le bundle Bootstrap embarqué par
Odoo.

Chez nous, "Meilleures ventes" (featured_products.xml) était depuis le
début une simple grille CSS statique affichant tous les produits d'un
coup, sans défilement.

Fix (reproduit à l'identique le comportement d'exocoms, avec nos
propres classes de carte .ch-product-card) :
- controllers/main.py (index()) : limit du fetch featured_products
  passé de 8 à 16.
- views/partials/featured_products.xml : les produits sont désormais
  découpés en lots de 4 (featured_chunks) et rendus dans un vrai
  carousel Bootstrap (.carousel/.carousel-inner/.carousel-item),
  défilement auto 5s, flèches précédent/suivant (masquées s'il n'y a
  qu'un seul lot).
- static/src/css/homepage.css : .ch-bestsellers-grid réutilisée PAR
  SLIDE (plus pour tous les produits d'un coup) + nouvelles classes
  .ch-bestsellers-carousel-wrap / .ch-bestsellers-arrow (flèches
  stylées avec la palette Capsule House).

Aucune donnée fabriquée : toujours les vrais produits publiés sur notre
site (même domaine de recherche qu'avant), simplement présentés en
carousel au lieu d'une grille figée.
"""
import logging

from odoo import api, SUPERUSER_ID

_logger = logging.getLogger(__name__)


def migrate(cr, version):
    from odoo.addons.capsule_house_theme import run_theme_maintenance

    env = api.Environment(cr, SUPERUSER_ID, {})
    _logger.info(
        "capsule_house_theme: post-migrate 19.0.1.0.102 — 'Meilleures "
        "ventes' reconstruite en vrai carousel Bootstrap 5 (lots de 4, "
        "auto 5s, flèches), même comportement que exocoms_theme "
        "(dashbord.xml, s_carousel_best), limit produits 8 -> 16."
    )
    run_theme_maintenance(env)
