# -*- coding: utf-8 -*-
"""
Rejoue run_theme_maintenance() après une mise à jour du module vers la
version 19.0.1.0.23.

Retour client : "et cla couleur orange en background" — sur la maquette
de référence, un halo orangé/pêche flouté déborde derrière la carte de
l'illustration hero. Ce halo n'a jamais été codé (oubli pur et simple,
pas un problème de données), d'où son absence sur le rendu réel.

Correctif 100% CSS (static/src/css/homepage.css) : ajout d'un
::before sur .ch-hero-visual (radial-gradient flouté, couleurs reprises
de la palette existante --ch-terracotta / --ch-salmon, z-index 0),
.ch-hero-visual passé en overflow: visible pour laisser le halo
déborder, .ch-hero-illustration et .ch-hero-float-card remontés en
z-index (1 et 2) pour rester au-dessus du halo. Aucune nouvelle donnée,
aucun template modifié.

Rejeu de run_theme_maintenance() ici uniquement par cohérence avec la
convention du module (comme pour le correctif CSS pur v19.0.1.0.21).
"""
import logging

from odoo import api, SUPERUSER_ID

_logger = logging.getLogger(__name__)


def migrate(cr, version):
    from odoo.addons.capsule_house_theme import run_theme_maintenance

    env = api.Environment(cr, SUPERUSER_ID, {})
    _logger.info(
        "capsule_house_theme: post-migrate 19.0.1.0.23 — halo orange "
        "flouté derrière l'illustration hero (CSS uniquement, absent "
        "du rendu initial car jamais codé)."
    )
    run_theme_maintenance(env)
