# -*- coding: utf-8 -*-
"""
Rejoue run_theme_maintenance() après une mise à jour du module vers la
version 19.0.1.0.28.

Retour client sur la v.27 (positionnement haut-droite correct) : "tu
vois la diff avec les deux" — comparaison de capture d'écran montrant
que le halo réel était trop compact/saturé, avec un bord visible
(presque une tache nette), alors que sur la maquette le halo est
beaucoup plus étalé et progressif, sans bord dur.

Correctif 100% CSS (static/src/css/homepage.css, .ch-hero-visual::before) :
- inset agrandi : top -30%, right -35%, bottom -12%, left -10% (au
  lieu de -18%/-22%/-6%/-6%)
- fondu repoussé beaucoup plus loin : salmon 30%, transparent 90% (au
  lieu de 50%/85%) pour un dégradé long au lieu d'un rond net
- flou renforcé : blur(55px) (au lieu de 35px)
- opacité réduite : 0.42 (au lieu de 0.6) pour une texture plus douce/
  pastel comme la maquette, moins saturée

Testé et confirmé visuellement EN DIRECT sur le site réel (override
CSS injecté via Claude in Chrome + capture d'écran de comparaison avec
la maquette) avant d'être reporté dans le code.
"""
import logging

from odoo import api, SUPERUSER_ID

_logger = logging.getLogger(__name__)


def migrate(cr, version):
    from odoo.addons.capsule_house_theme import run_theme_maintenance

    env = api.Environment(cr, SUPERUSER_ID, {})
    _logger.info(
        "capsule_house_theme: post-migrate 19.0.1.0.28 — halo hero "
        "élargi et adouci (fondu/flou/opacité) pour matcher la texture "
        "diffuse de la maquette au lieu d'un blob compact et saturé."
    )
    run_theme_maintenance(env)
