# -*- coding: utf-8 -*-
"""
Rejoue run_theme_maintenance() après une mise à jour du module vers la
version 19.0.1.0.17.

Suite à l'audit systématique complet demandé par le client (comparaison
fichier par fichier avec exocoms_theme, plutôt que de découvrir chaque
écart au coup par coup) : gap trouvé dans __init__.py — aucune fonction
n'activait jamais de deuxième langue sur le site. Le sélecteur de
langue natif du header (header.xml/layout.css), pourtant explicitement
demandé, ne s'affiche que si `len(request.website.language_ids) > 1` :
sans activation, il restait construit mais invisible.

Nouvelle fonction `_setup_languages(env, website)` (même pattern que
exocoms_theme._setup_languages) : active fr_FR + en_US, fr_FR par
défaut. Idempotent, rejouable depuis le cron horaire.

Rejeu de run_theme_maintenance() ici pour que le sélecteur de langue
s'affiche dès cette mise à jour.
"""
import logging

from odoo import api, SUPERUSER_ID

_logger = logging.getLogger(__name__)


def migrate(cr, version):
    from odoo.addons.capsule_house_theme import run_theme_maintenance

    env = api.Environment(cr, SUPERUSER_ID, {})
    _logger.info(
        "capsule_house_theme: post-migrate 19.0.1.0.17 — activation "
        "fr_FR + en_US (corrige le sélecteur de langue du header, "
        "jusqu'ici invisible faute de deuxième langue active)."
    )
    run_theme_maintenance(env)
