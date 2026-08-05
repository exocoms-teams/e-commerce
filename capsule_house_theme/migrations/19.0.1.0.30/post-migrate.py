# -*- coding: utf-8 -*-
"""
Rejoue run_theme_maintenance() après une mise à jour du module vers la
version 19.0.1.0.30.

Retour client : "comment l'autre occupe l'écran par rapport au mien"
— comparaison à cadrage égal (capture recadrée sur la seule colonne
visuelle, comme la maquette de référence) : le halo du modèle "lave"
quasiment tout le fond de la carte, même dans le coin opposé à sa
concentration (fondu ambiant très large), alors que le nôtre restait
contenu au coin haut-droite et retombait au blanc pur dès le milieu du
cadre.

Correctif 100% CSS (static/src/css/homepage.css, .ch-hero-visual::before) :
inset encore agrandi sur les 4 côtés (top -70%, right -80%, left -60%,
bottom -60% — au lieu de -55%/-65%/-15%/-20%), fondu repoussé à
22%/78%, blur(70px) (au lieu de 60px), opacity 0.4 (au lieu de 0.45).

Testé et confirmé EN DIRECT sur le site réel avant d'être committé :
override CSS injecté via Claude in Chrome, capture d'écran recadrée
exactement comme la maquette de référence pour comparaison directe.
"""
import logging

from odoo import api, SUPERUSER_ID

_logger = logging.getLogger(__name__)


def migrate(cr, version):
    from odoo.addons.capsule_house_theme import run_theme_maintenance

    env = api.Environment(cr, SUPERUSER_ID, {})
    _logger.info(
        "capsule_house_theme: post-migrate 19.0.1.0.30 — halo hero "
        "élargi pour couvrir tout le fond de la carte (occupation du "
        "cadre alignée sur la maquette), vérifié en direct."
    )
    run_theme_maintenance(env)
