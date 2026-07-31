# -*- coding: utf-8 -*-
"""
Rejoue run_theme_maintenance() après une mise à jour du module vers la
version 19.0.1.0.31.

Retour client sur la v.30 (bonne couverture du cadre) : "il faut que
ce soit aussi visible que sur le modèle" — la couleur restait trop
pâle malgré une bonne largeur de couverture.

Correctif 100% CSS (static/src/css/homepage.css, .ch-hero-visual::before) :
- opacity 0.4 -> 0.65
- filter: blur(70px) -> blur(55px) (moins de flou = couleur plus lisible)
- fondu resserré : salmon 30% / transparent 82% (au lieu de 22%/78%)

Inset inchangé (top -70%, right -80%, left -60%, bottom -60%) — la
largeur de couverture obtenue en v.30 était correcte, seule
l'intensité manquait.

Testé et confirmé EN DIRECT sur le site réel avant d'être committé :
override CSS injecté via Claude in Chrome, capture recadrée comme la
maquette pour comparaison directe.
"""
import logging

from odoo import api, SUPERUSER_ID

_logger = logging.getLogger(__name__)


def migrate(cr, version):
    from odoo.addons.capsule_house_theme import run_theme_maintenance

    env = api.Environment(cr, SUPERUSER_ID, {})
    _logger.info(
        "capsule_house_theme: post-migrate 19.0.1.0.31 — halo hero "
        "plus intense/visible (opacity + blur + fondu ajustés) pour "
        "matcher la maquette, vérifié en direct."
    )
    run_theme_maintenance(env)
