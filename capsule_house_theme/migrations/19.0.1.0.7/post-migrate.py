# -*- coding: utf-8 -*-
"""
Rejoue run_theme_maintenance() après une mise à jour du module vers la
version 19.0.1.0.7.

Deux correctifs XML/CSS dans cette version :

1. views/templates/footer.xml : ajout des liens "Nouveautés" (tri par date
   de création décroissante sur /shop) et "Accessoires" (lien réel vers la
   catégorie du même nom, seulement si elle existe déjà pour notre site —
   jamais de lien en dur vers un id qui pourrait ne pas exister). Il
   manquait par rapport à la maquette de référence.

2. static/src/css/homepage.css : .ch-hero-grid utilise désormais
   `grid-template-areas` + `grid-area` explicite sur `.ch-hero-content`/
   `.ch-hero-visual` plutôt que de compter uniquement sur l'auto-placement
   CSS Grid par ordre du DOM — diagnostiqué en conditions réelles : le
   texte du hero apparaissait dans la colonne de droite avec la gauche
   vide. Ce correctif rend le placement des deux colonnes explicite et
   indépendant de tout style hérité (direction, etc.) qui pourrait
   perturber l'auto-placement par défaut.
"""
import logging

from odoo import api, SUPERUSER_ID

_logger = logging.getLogger(__name__)


def migrate(cr, version):
    from odoo.addons.capsule_house_theme import run_theme_maintenance

    env = api.Environment(cr, SUPERUSER_ID, {})
    _logger.info(
        "capsule_house_theme: post-migrate 19.0.1.0.7 — rejeu de "
        "run_theme_maintenance() (liens footer Nouveautés/Accessoires + "
        "grid-area explicite sur le hero)."
    )
    run_theme_maintenance(env)
