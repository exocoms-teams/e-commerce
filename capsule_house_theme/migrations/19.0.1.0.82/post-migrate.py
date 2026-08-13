# -*- coding: utf-8 -*-
"""
Rejoue run_theme_maintenance() après une mise à jour du module vers la
version 19.0.1.0.82.

Le correctif d'espacement de la 19.0.1.0.81 (margin-top 48px avant
chaque titre de section sur /nos-gammes/<slug>) a été déployé par le
client mais restait visuellement trop serré ("regarde les grands
titres c'est trop collé vers le haut", capture d'écran à l'appui —
"Technical specifications" et "Options" quasiment sans espace visible).

Cause probable : margin-top peut fusionner (collapse) avec la marge
basse du bloc précédent, donnant un écart réellement affiché plus
petit que la valeur déclarée. Remplacé par padding-top (jamais sujet à
fusion de marges) fixé à 64px, avec la ligne de séparation
(border-top) conservée en haut de cet espace. Le premier titre de
chaque page (Formats) reste sans espace ni ligne
(:first-of-type, inchangé).

Fichier modifié : static/src/css/pages.css uniquement.
"""
import logging

from odoo import api, SUPERUSER_ID

_logger = logging.getLogger(__name__)


def migrate(cr, version):
    from odoo.addons.capsule_house_theme import run_theme_maintenance

    env = api.Environment(cr, SUPERUSER_ID, {})
    _logger.info(
        "capsule_house_theme: post-migrate 19.0.1.0.82 — espacement des "
        "titres de section de /nos-gammes/<slug> passé de margin-top 48px "
        "(pouvait fusionner avec la marge du bloc précédent) à padding-top "
        "64px garanti."
    )
    run_theme_maintenance(env)
