# -*- coding: utf-8 -*-
"""
Rejoue run_theme_maintenance() après une mise à jour du module vers la
version 19.0.1.0.27.

Retour client sur la v.26 (halo enfin visible) : "mais il doit être
placé comme sur le modèle" — sur la maquette de référence, le halo
n'est pas centré/symétrique autour de la carte, il est concentré en
haut à droite (comme une source de lumière), plus discret en bas à
gauche.

Correctif 100% CSS (static/src/css/homepage.css, .ch-hero-visual::before) :
- inset asymétrique : top -18%, right -22%, bottom -6%, left -6%
  (débordement nettement plus grand en haut/à droite qu'en bas/à
  gauche)
- centre du radial-gradient décalé : `at 68% 32%` (au lieu de 50% 50%
  implicite), pour que le cœur le plus intense du halo soit lui aussi
  vers le haut-droite
- fondu ajusté à 50%/85%

Testé et confirmé visuellement EN DIRECT sur le site réel (override
CSS injecté via Claude in Chrome + capture d'écran de comparaison avec
la maquette) avant d'être reporté dans le code. Toujours aucune donnée
ni template touchés.
"""
import logging

from odoo import api, SUPERUSER_ID

_logger = logging.getLogger(__name__)


def migrate(cr, version):
    from odoo.addons.capsule_house_theme import run_theme_maintenance

    env = api.Environment(cr, SUPERUSER_ID, {})
    _logger.info(
        "capsule_house_theme: post-migrate 19.0.1.0.27 — halo hero "
        "repositionné en haut à droite comme sur la maquette (inset "
        "asymétrique + centre de gradient décalé)."
    )
    run_theme_maintenance(env)
