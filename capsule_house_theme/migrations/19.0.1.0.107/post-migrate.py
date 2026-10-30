# -*- coding: utf-8 -*-
"""
Rejoue run_theme_maintenance() après une mise à jour du module vers la
version 19.0.1.0.107.

CH-135 — Harmonisation de la présentation des pages des cinq gammes.
Cette évolution concerne les vues frontend ; le hook de maintenance
du module est rejoué conformément à sa convention de migration.
"""
import logging

from odoo import api, SUPERUSER_ID

_logger = logging.getLogger(__name__)


def migrate(cr, version):
    from odoo.addons.capsule_house_theme import run_theme_maintenance

    env = api.Environment(cr, SUPERUSER_ID, {})
    _logger.info(
        "capsule_house_theme: post-migrate 19.0.1.0.107 — "
        "CH-135 — harmonisation des pages Cabine, Dôme, Modulaire, Pliable et Capsule."
    )
    run_theme_maintenance(env)
