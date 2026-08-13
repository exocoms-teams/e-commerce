# -*- coding: utf-8 -*-
"""
Rejoue run_theme_maintenance() après une mise à jour du module vers la
version 19.0.1.0.80.

Ajoute la section "Performances" à la page détail de gamme
(/nos-gammes/<slug>) — demande client, capture d'écran de
capsule-home.fr/1-capsule.html à l'appui : "tu as oublié performances
et j'ai aussi le design de la page" (confirmation que le design général
de la page convient).

9 points forts pour la gamme Capsule (GAMMES_DATA, __init__.py, clé
`performances`) : vitrage isolant, serrure sécurisée, éclairage LED
encastré, salle de bain équipée, puits de lumière, design aluminium,
alimentation électrique, escalier 3 marches, structure solide — repris
de la structure de la page de référence, en gardant les normes réelles
déjà utilisées ailleurs sur cette même page (NF EN 1279, NF C 15-100)
pour rester cohérent. Positionnée en tête de contenu, avant la section
Formats — même ordre que la page de référence. Liste vide pour les 4
autres gammes (Cabine/Dôme/Modulaire/Pliable), toujours sans contenu
réel.

Fichiers modifiés : __init__.py (GAMMES_DATA), nos_gammes.xml (nouvelle
section), pages.css (.ch-gamme-perf-*).
"""
import logging

from odoo import api, SUPERUSER_ID

_logger = logging.getLogger(__name__)


def migrate(cr, version):
    from odoo.addons.capsule_house_theme import run_theme_maintenance

    env = api.Environment(cr, SUPERUSER_ID, {})
    _logger.info(
        "capsule_house_theme: post-migrate 19.0.1.0.80 — section "
        "'Performances' ajoutée en tête de la page détail de gamme (9 "
        "points forts pour Capsule), avant la section Formats."
    )
    run_theme_maintenance(env)
