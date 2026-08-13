# -*- coding: utf-8 -*-
"""
Rejoue run_theme_maintenance() après une mise à jour du module vers la
version 19.0.1.0.81.

Corrige deux problèmes de mise en page relevés par le client sur
/nos-gammes/<slug> ("c'est pas trop serré et le design tu trouves ça
bien ?") :

1. Espacement entre sections trop faible — .ch-gamme-section-title
   passe de margin-top 32px à 48px, avec un padding-top de 24px et une
   ligne de séparation (border-top) pour marquer clairement le début
   de chaque nouvelle section. Le premier titre de la page (Formats)
   n'a ni marge ni ligne (règle :first-of-type dédiée).
2. Grille "Équipements inclus" en auto-fit (colonnes variables selon la
   longueur du texte) remplacée par une grille à 2 colonnes fixes,
   plus régulière visuellement (repasse à 1 colonne sous 560px).

Fichier modifié : static/src/css/pages.css uniquement, aucun changement
de contenu (GAMMES_DATA inchangée).
"""
import logging

from odoo import api, SUPERUSER_ID

_logger = logging.getLogger(__name__)


def migrate(cr, version):
    from odoo.addons.capsule_house_theme import run_theme_maintenance

    env = api.Environment(cr, SUPERUSER_ID, {})
    _logger.info(
        "capsule_house_theme: post-migrate 19.0.1.0.81 — espacement entre "
        "sections de la page détail de gamme augmenté (32px -> 48px + "
        "ligne de séparation), grille équipements passée en 2 colonnes "
        "fixes au lieu d'auto-fit."
    )
    run_theme_maintenance(env)
