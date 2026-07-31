# -*- coding: utf-8 -*-
"""
Rejoue run_theme_maintenance() après une mise à jour du module vers la
version 19.0.1.0.45.

Retour client : "l'écart entre les deux est un peu trop grand, tu ne
trouves si tu pouvais juste réduire un peu" (capture montrant le grand
espace blanc entre la ligne de confiance du hero et "Meilleures
ventes").

Écart total = padding-bottom de .ch-hero (72px) + padding-top de
.ch-bestsellers (64px) = 136px. Réduit en miroir sur les deux :
.ch-hero padding-bottom 72px -> 48px, .ch-bestsellers padding-top
64px -> 40px (nouvel écart total : 88px). Les autres paddings
(haut du hero, bas de la section ventes) inchangés.
"""
import logging

from odoo import api, SUPERUSER_ID

_logger = logging.getLogger(__name__)


def migrate(cr, version):
    from odoo.addons.capsule_house_theme import run_theme_maintenance

    env = api.Environment(cr, SUPERUSER_ID, {})
    _logger.info(
        "capsule_house_theme: post-migrate 19.0.1.0.45 — écart réduit "
        "entre le hero et 'Meilleures ventes' (136px -> 88px)."
    )
    run_theme_maintenance(env)
