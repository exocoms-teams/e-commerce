# -*- coding: utf-8 -*-
"""
Rejoue run_theme_maintenance() après une mise à jour du module vers la
version 19.0.1.0.34.

Retour client sur la v.33, avec une capture annotée à la main : un
trait ROUGE dessinant l'étendue exacte voulue du halo, comparé au trait
GRIS (étendue actuelle de la v.33 rappelée sur la même image). Le trait
rouge démarre nettement plus à gauche en haut du cadre (juste au-dessus
du bord gauche de la carte) alors que le gris ne commençait qu'après
la moitié de la largeur de la carte — tout le quart supérieur-gauche
restait blanc, sans aucune trace de halo.

Correctif 100% CSS (static/src/css/homepage.css, .ch-hero-visual::before) :
- left: -90% (au lieu de -50%) : débordement à gauche fortement
  augmenté, le halo s'étend maintenant visiblement au-dessus/à gauche
  du bloc de texte du hero, pas seulement derrière l'illustration
- bottom: -55% (au lieu de -50%), léger ajustement pour rester cohérent
  avec le bas du trait rouge
- centre du dégradé recentré : `at 58% 32%` (au lieu de `64% 30%`),
  pour laisser plus de place au débordement gauche tout en gardant
  l'intensité concentrée en haut à droite

Testé et confirmé EN DIRECT sur le site réel (capture plein écran,
avec le texte du hero visible) avant d'être committé.
"""
import logging

from odoo import api, SUPERUSER_ID

_logger = logging.getLogger(__name__)


def migrate(cr, version):
    from odoo.addons.capsule_house_theme import run_theme_maintenance

    env = api.Environment(cr, SUPERUSER_ID, {})
    _logger.info(
        "capsule_house_theme: post-migrate 19.0.1.0.34 — halo hero "
        "étendu vers la gauche (débordement au-dessus du texte hero), "
        "suite à une capture annotée à la main par le client."
    )
    run_theme_maintenance(env)
