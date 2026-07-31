# -*- coding: utf-8 -*-
"""
Rejoue run_theme_maintenance() après une mise à jour du module vers la
version 19.0.1.0.9.

Remplace les deux illustrations en CSS pur par les SVG exacts validés par
le client (fournis tels quels, ne pas régénérer) :
- header.xml : badge/logo circulaire (remplace .ch-logo-mark en CSS pur).
- hero.xml : illustration du pod (remplace .ch-pod-shape/.ch-pod-circle-*
  + le pseudo-élément d'ombre au sol ajouté en 19.0.1.0.8 — l'ombre est
  désormais incluse directement dans le SVG).

Toutes les couleurs utilisées dans ces deux SVG correspondaient déjà
exactement aux variables --ch-* de variables.css (aucun ajustement de
palette nécessaire) : #F6B26B=--ch-amber, #C1694F=--ch-terracotta,
#EDE0D0=--ch-tan-2, #EAD9C4=--ch-tan-1, #FFF3E0=--ch-highlight,
#E3A48A=--ch-salmon, #1F2421=--ch-ink.
"""
import logging

from odoo import api, SUPERUSER_ID

_logger = logging.getLogger(__name__)


def migrate(cr, version):
    from odoo.addons.capsule_house_theme import run_theme_maintenance

    env = api.Environment(cr, SUPERUSER_ID, {})
    _logger.info(
        "capsule_house_theme: post-migrate 19.0.1.0.9 — rejeu de "
        "run_theme_maintenance() (SVG logo + SVG illustration pod validés "
        "par le client)."
    )
    run_theme_maintenance(env)
