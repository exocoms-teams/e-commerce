# -*- coding: utf-8 -*-
"""
Rejoue run_theme_maintenance() après une mise à jour du module vers la
version 19.0.1.0.44.

Retour client (capture de la pagination boutique) : "tu as oublié la
couleur ici comme on a fait dans exocoms_theme" — le rond de la page
active du pager natif Odoo (#o_wsale_pager) restait sur le violet par
défaut d'Odoo (#875A7B) au lieu du terracotta de la marque.

Vérifié dans exocoms_theme/static/src/css/layout.css : ils ont
exactement cette même règle, scopée à #o_wsale_pager, recolorée en
bleu (leur marque). Reprise à l'identique dans shop.css avec
--ch-terracotta / --ch-white à la place.
"""
import logging

from odoo import api, SUPERUSER_ID

_logger = logging.getLogger(__name__)


def migrate(cr, version):
    from odoo.addons.capsule_house_theme import run_theme_maintenance

    env = api.Environment(cr, SUPERUSER_ID, {})
    _logger.info(
        "capsule_house_theme: post-migrate 19.0.1.0.44 — couleur "
        "terracotta appliquée à la pagination boutique (#o_wsale_pager), "
        "d'après exocoms_theme."
    )
    run_theme_maintenance(env)
