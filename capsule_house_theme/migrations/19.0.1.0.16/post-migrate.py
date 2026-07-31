# -*- coding: utf-8 -*-
"""
Rejoue run_theme_maintenance() après une mise à jour du module vers la
version 19.0.1.0.16.

Ajout d'une route `/boutique` (controllers/main.py), alias FR de /shop,
même route que sur exocoms_theme — simple redirect HTTP vers la page
boutique native, aucune donnée à migrer. Rejeu de
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
        "capsule_house_theme: post-migrate 19.0.1.0.16 — ajout de la "
        "route /boutique (alias de /shop, comme sur exocoms_theme)."
    )
    run_theme_maintenance(env)
