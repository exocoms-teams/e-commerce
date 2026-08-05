# -*- coding: utf-8 -*-
"""
Rejoue run_theme_maintenance() après une mise à jour du module vers la
version 19.0.1.0.33.

Retour client sur la v.32 : le contour était bien net mais le halo
était redevenu trop petit (visible seulement en haut) ET trop
foncé/saturé — la v.32 avait resserré la TAILLE en même temps que le
contour, ce qui n'était pas demandé. Le client rappelle que les traits
tracés à la main sur la maquette montrent une zone couvrant plus de la
moitié du cadre.

Correctif 100% CSS (static/src/css/homepage.css, .ch-hero-visual::before) :
- inset rétabli large, proche de la v.30 : top -65%, right -75%,
  left -50%, bottom -50% (au lieu de -45%/-55%/-25%/-30% en v.32)
- fondu gardé resserré (35%/70%, proche de la v.32) pour conserver le
  contour net demandé
- opacity réduite à 0.4 (au lieu de 0.6) pour une couleur plus claire,
  moins "foncée"
- blur(48px) (entre le 38px trop net de la v.32 et le 55-70px trop
  diffus des v.30/.31)

Objectif : grande couverture (plus de la moitié du cadre) + contour
repérable + couleur claire, les 3 exigences client réunies en même
temps (jusqu'ici corrigées une par une en régressant sur les autres).

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
        "capsule_house_theme: post-migrate 19.0.1.0.33 — halo hero "
        "réajusté pour combiner grande couverture + contour net + "
        "couleur claire (les 3 retours client réunis), vérifié en direct."
    )
    run_theme_maintenance(env)
