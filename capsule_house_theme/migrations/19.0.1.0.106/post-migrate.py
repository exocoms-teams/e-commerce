# -*- coding: utf-8 -*-
"""
Rejoue run_theme_maintenance() après une mise à jour du module vers la
version 19.0.1.0.106.

CH-31 — Mise en place du blog / actualités avec le module natif
website_blog. Le hook de maintenance permet notamment de resynchroniser
le menu de navigation du site après l'installation ou la mise à jour
du module.
"""
import logging

from odoo import api, SUPERUSER_ID

_logger = logging.getLogger(__name__)


def migrate(cr, version):
    from odoo.addons.capsule_house_theme import run_theme_maintenance

    env = api.Environment(cr, SUPERUSER_ID, {})
    _logger.info(
        "capsule_house_theme: post-migrate 19.0.1.0.106 — "
        "CH-31 blog / actualités avec le module natif website_blog."
    )
    run_theme_maintenance(env)
