# -*- coding: utf-8 -*-
"""
Rejoue run_theme_maintenance() après une mise à jour du module vers la
version 19.0.1.0.103.

DEMANDE CLIENT : "il faut que pour chaque gamme au niveau de leur hero
il y a un bouton qui les envoie directement à la catégorie
correspondant du filmstrip" — le filmstrip de catégories natif d'Odoo
sur /shop (voir SHOP_CATEGORIES / _setup_shop_categories dans
setup_utils.py : nos 5 gammes sont déjà les 5 catégories boutique de
premier niveau).

Fix :
- controllers/main.py (nos_gammes_detail()) : résout la VRAIE catégorie
  boutique (product.public.category) de même nom que la gamme, avec
  exactement le même domaine de recherche que _setup_shop_categories()
  (nom + website_id scopé/global). Construit shop_category_url
  ('/shop/category/<slug>') seulement si la catégorie existe réellement
  — jamais un lien fabriqué/mort.
- views/pages/nos_gammes.xml : nouveau bouton "Voir dans la boutique" /
  "View in shop" dans le hero de chaque page /nos-gammes/<slug>, masqué
  si shop_category_url est vide.
- static/src/css/pages.css : .ch-gamme-hero-actions (espacement),
  réutilise les classes .ch-btn/.ch-btn-primary déjà existantes.

Aucune donnée fabriquée : le bouton n'apparaît que si la catégorie
boutique correspondante existe vraiment sur le site (créée par
_setup_shop_categories(), déjà rejouée par ce même run_theme_maintenance
plus bas dans la séquence).
"""
import logging

from odoo import api, SUPERUSER_ID

_logger = logging.getLogger(__name__)


def migrate(cr, version):
    from odoo.addons.capsule_house_theme import run_theme_maintenance

    env = api.Environment(cr, SUPERUSER_ID, {})
    _logger.info(
        "capsule_house_theme: post-migrate 19.0.1.0.103 — bouton 'Voir "
        "dans la boutique' ajouté au hero de chaque page /nos-gammes/"
        "<slug>, renvoyant vers la vraie catégorie boutique "
        "correspondante (filmstrip /shop)."
    )
    run_theme_maintenance(env)
