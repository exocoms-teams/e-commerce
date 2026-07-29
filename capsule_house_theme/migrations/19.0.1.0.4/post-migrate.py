# -*- coding: utf-8 -*-
"""
Rejoue run_theme_maintenance() après une mise à jour du module vers la
version 19.0.1.0.4.

Correctif purement XML (views/pages/home.xml) : ajout de la classe
oe_structure sur #wrap pour permettre l'insertion/réorganisation de blocs
natifs depuis le panneau "Blocks" du website builder, sur la page
d'accueil. S'applique automatiquement à la mise à jour (les vues sont
rechargées à chaque -u) ; ce dossier est dupliqué par cohérence avec la
règle du README ("à chaque bump de version").
"""
import logging

from odoo import api, SUPERUSER_ID

_logger = logging.getLogger(__name__)


def migrate(cr, version):
    from odoo.addons.capsule_house_theme import run_theme_maintenance

    env = api.Environment(cr, SUPERUSER_ID, {})
    _logger.info(
        "capsule_house_theme: post-migrate 19.0.1.0.4 — rejeu de "
        "run_theme_maintenance() (correctif principal purement XML, voir "
        "views/pages/home.xml)."
    )
    run_theme_maintenance(env)
