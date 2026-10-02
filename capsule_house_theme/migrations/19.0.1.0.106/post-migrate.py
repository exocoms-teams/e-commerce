# -*- coding: utf-8 -*-
"""Apply the native contact page integration after upgrading the theme."""
import logging

from odoo import api, SUPERUSER_ID

_logger = logging.getLogger(__name__)


def migrate(cr, version):
    from odoo.addons.capsule_house_theme import run_theme_maintenance

    env = api.Environment(cr, SUPERUSER_ID, {})
    _logger.info(
        "capsule_house_theme: post-migrate 19.0.1.0.106 — native contact "
        "page integrated into Company navigation and scoped to its website."
    )
    run_theme_maintenance(env)