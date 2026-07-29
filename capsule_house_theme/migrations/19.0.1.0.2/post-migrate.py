# -*- coding: utf-8 -*-
"""
Rejoue run_theme_maintenance() après une mise à jour du module vers la
version 19.0.1.0.2.

Cette version ajoute _attach_shop_filters_to_products() : rattache
l'attribut filtre 'Surface (m²)' aux produits publiés du site, sans quoi
il resterait invisible dans la sidebar boutique (leçon reprise du module
de référence exocoms_theme — _attach_monetique_attributes_to_products —
qui a rencontré exactement ce bug : un attribut créé comme catalogue
global n'apparaît comme filtre que s'il est aussi porté par au moins un
product.template.attribute_line_ids).

Règle à respecter à CHAQUE bump de version dans __manifest__.py : dupliquer
ce dossier sous `migrations/<nouvelle_version>/post-migrate.py` (même
contenu, il suffit d'appeler run_theme_maintenance).
"""
import logging

from odoo import api, SUPERUSER_ID

_logger = logging.getLogger(__name__)


def migrate(cr, version):
    from odoo.addons.capsule_house_theme import run_theme_maintenance

    env = api.Environment(cr, SUPERUSER_ID, {})
    _logger.info(
        "capsule_house_theme: post-migrate 19.0.1.0.2 — rejeu de "
        "run_theme_maintenance() (inclut le rattachement du filtre "
        "'Surface (m²)' aux produits)."
    )
    run_theme_maintenance(env)
