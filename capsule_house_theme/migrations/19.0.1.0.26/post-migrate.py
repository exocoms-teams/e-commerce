# -*- coding: utf-8 -*-
"""
Rejoue run_theme_maintenance() après une mise à jour du module vers la
version 19.0.1.0.26.

Deux choses corrigées ici :

1) Le manifest local était repassé à 'version': '1.0' (probablement en
   testant la question "pourquoi pas juste mettre 1.0"). Remis à
   19.0.1.0.26 avant que ça n'atteigne le site réel — cf. l'avertissement
   en tête de __manifest__.py : ce format casse la comparaison de
   version qu'Odoo utilise pour savoir quels dossiers migrations/
   rejouer.

2) Vrai correctif du halo hero (celui qui restait invisible depuis la
   v19.0.1.0.22, malgré plusieurs essais d'opacité/flou/inset). Cause
   confirmée par inspection live du DOM sur le site réel (getComputedStyle
   + capture d'écran), pas devinée : avec un radial-gradient
   `closest-side` (cercle ou ellipse) et un fondu vers transparent à
   68%, le rayon effectivement "coloré" du dégradé restait plus petit
   que le demi-côté de la carte elle-même — tout le halo se retrouvait
   donc caché DERRIÈRE la carte, seul un infime liseré flouté dépassait.
   Aucun réglage d'opacité/flou ne pouvait corriger ça, c'était un
   problème de géométrie, pas de couleur.

   Correctif testé et validé EN DIRECT (override CSS injecté dans la
   page live, capture d'écran de confirmation) avant d'être reporté
   dans static/src/css/homepage.css :
   - ellipse (pas cercle forcé) pour suivre la forme de la carte
   - fondu repoussé à 55%/88% (au lieu de 40%/68%) pour que la couleur
     dépasse réellement des 4 côtés
   - opacity 0.6, blur(35px)
"""
import logging

from odoo import api, SUPERUSER_ID

_logger = logging.getLogger(__name__)


def migrate(cr, version):
    from odoo.addons.capsule_house_theme import run_theme_maintenance

    env = api.Environment(cr, SUPERUSER_ID, {})
    _logger.info(
        "capsule_house_theme: post-migrate 19.0.1.0.26 — halo hero "
        "enfin visible (fondu du gradient repoussé à 55%%/88%%, cause "
        "géométrique confirmée par inspection live du DOM, pas devinée)."
    )
    run_theme_maintenance(env)
