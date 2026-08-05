# -*- coding: utf-8 -*-
"""
Rejoue run_theme_maintenance() après une mise à jour du module vers la
version 19.0.1.0.25.

Le halo (v19.0.1.0.24) était bien visible et orangé (bon retour client :
"l'effet est plutôt cool"), mais retour suivant : "je veux que ça soit
comme sur le modèle" — sur la capture réelle il paraissait concentré en
haut à droite plutôt que centré/symétrique autour de toute la carte
comme sur la maquette.

Cause : `.ch-hero-visual::before` utilisait un inset asymétrique
(-14% haut/bas, -8% gauche/droite) combiné à un radial-gradient
`closest-side` sans mot-clé `circle`, qui dessine une ellipse calée
sur la forme du bloc (rectangle plus large que haut) plutôt qu'un
cercle homogène.

Correctif 100% CSS (static/src/css/homepage.css) :
- inset uniforme (-20% sur les 4 côtés au lieu de -14%/-8%)
- radial-gradient(circle closest-side, ...) : cercle vrai, centré,
  plutôt qu'une ellipse asymétrique

Toujours aucune donnée ni template touchés.
"""
import logging

from odoo import api, SUPERUSER_ID

_logger = logging.getLogger(__name__)


def migrate(cr, version):
    from odoo.addons.capsule_house_theme import run_theme_maintenance

    env = api.Environment(cr, SUPERUSER_ID, {})
    _logger.info(
        "capsule_house_theme: post-migrate 19.0.1.0.25 — halo hero "
        "recentré en cercle symétrique (inset uniforme + "
        "radial-gradient circle), suite retour client sur v.24."
    )
    run_theme_maintenance(env)
