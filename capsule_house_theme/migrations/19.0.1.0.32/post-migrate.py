# -*- coding: utf-8 -*-
"""
Rejoue run_theme_maintenance() après une mise à jour du module vers la
version 19.0.1.0.32.

Retour client sur la v.31 : "non pas concentré comme ça, laisse
tomber" puis deux captures annotées à la main (traits tracés sur la
maquette ET sur notre rendu) pour clarifier le vrai problème : le halo
du modèle a un BORD repérable — une limite qu'on peut suivre, même
douce — alors que le nôtre (v.30/.31), trop flouté sur une zone trop
large, n'avait plus de forme du tout, juste un dégradé infini sans
limite perceptible.

Correctif 100% CSS (static/src/css/homepage.css, .ch-hero-visual::before) :
- inset resserré : top -45%, right -55%, left -25%, bottom -30% (au
  lieu de -70%/-80%/-60%/-60%)
- fondu resserré : salmon 42%, transparent 72% (au lieu de 30%/82%)
- flou réduit : blur(38px) (au lieu de 55px)
- opacity 0.6 (quasi inchangée, 0.65 -> 0.6)

Objectif : retrouver un contour net et traçable tout en gardant une
bonne couverture et une bonne intensité (pas de retour à un halo
invisible comme sur les toutes premières versions).

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
        "capsule_house_theme: post-migrate 19.0.1.0.32 — halo hero "
        "resserré pour retrouver un contour net et traçable (au lieu "
        "d'un dégradé infini sans forme), vérifié en direct."
    )
    run_theme_maintenance(env)
