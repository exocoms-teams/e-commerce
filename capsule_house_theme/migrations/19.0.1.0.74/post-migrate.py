# -*- coding: utf-8 -*-
"""
Rejoue run_theme_maintenance() après une mise à jour du module vers la
version 19.0.1.0.74.

Retire le bandeau de pastilles Studio/Duo/Panorama/Accessoires en haut
de la page /nos-modeles (views/pages/nos_modeles.xml, section
ch-models-hero) — demande client explicite après capture d'écran :
"ils ne doivent plus apparaître puisque ce sont juste des formats pour
nos gammes, pas une catégorie du filmstrip".

Contexte : Studio/Duo/Panorama sont désormais des FORMATS au sein de la
gamme "Capsule" (GAMMES_DATA, __init__.py, page /nos-gammes/capsule
depuis la 19.0.1.0.71) — les afficher encore comme des catégories à
elles seules sur /nos-modeles contredit cette nouvelle taxonomie, même
si la page /nos-modeles elle-même reste conservée par ailleurs (demande
client explicite, confirmée à plusieurs reprises : "on laisse nos
modèles"). Seul ce bandeau de tags est retiré ; la grille de 4 cartes
plus bas sur la page (avec images/descriptions) n'est pas modifiée.
"""
import logging

from odoo import api, SUPERUSER_ID

_logger = logging.getLogger(__name__)


def migrate(cr, version):
    from odoo.addons.capsule_house_theme import run_theme_maintenance

    env = api.Environment(cr, SUPERUSER_ID, {})
    _logger.info(
        "capsule_house_theme: post-migrate 19.0.1.0.74 — bandeau de "
        "pastilles Studio/Duo/Panorama/Accessoires retiré du hero de "
        "/nos-modeles (formats de la gamme Capsule, plus des catégories "
        "affichées comme telles ici) ; grille de cartes plus bas inchangée."
    )
    run_theme_maintenance(env)
