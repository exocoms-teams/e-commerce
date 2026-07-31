# -*- coding: utf-8 -*-
"""
Rejoue run_theme_maintenance() après une mise à jour du module vers la
version 19.0.1.0.24.

Retour client sur v19.0.1.0.23 : "il y a pas toujours cette couleur
derrière comme sur le modèle" — le halo ajouté en .23 était trop pâle
et délavé (opacity 0.32 + blur 60px + fondu à 72% le rendaient presque
gris/beige au lieu d'orange/pêche visible comme sur la maquette).

Correctif 100% CSS (static/src/css/homepage.css, .ch-hero-visual::before) :
- opacity 0.32 -> 0.55
- filter: blur(60px) -> blur(40px) (moins de flou = couleur plus lisible)
- fondu du gradient resserré (salmon à 40% au lieu de 45%, transparent
  à 68% au lieu de 72%) pour garder une teinte orangée plus franche sur
  une plus grande partie du halo
- inset resserré de -18%/-12% à -14%/-8% pour ne pas trop diluer la
  couleur sur une zone excessive

Toujours aucune donnée ni template touchés. Rejeu de
run_theme_maintenance() par cohérence de convention (correctif CSS
pur).
"""
import logging

from odoo import api, SUPERUSER_ID

_logger = logging.getLogger(__name__)


def migrate(cr, version):
    from odoo.addons.capsule_house_theme import run_theme_maintenance

    env = api.Environment(cr, SUPERUSER_ID, {})
    _logger.info(
        "capsule_house_theme: post-migrate 19.0.1.0.24 — halo hero "
        "rendu plus visible/orangé (opacity + blur + fondu du "
        "gradient ajustés, suite retour client sur v.23)."
    )
    run_theme_maintenance(env)
