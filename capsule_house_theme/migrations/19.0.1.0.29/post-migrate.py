# -*- coding: utf-8 -*-
"""
Rejoue run_theme_maintenance() après une mise à jour du module vers la
version 19.0.1.0.29.

Retour client sur la v.28 avec 2 captures comparatives : "ne vois-tu
pas la grandeur du halo du modèle par rapport au mien, je veux que ce
soit exactement pareil" — le halo du modèle occupe une zone nettement
plus grande (s'étend beaucoup plus loin de la carte) que le nôtre à
taille de carte égale.

Correctif 100% CSS (static/src/css/homepage.css, .ch-hero-visual::before) :
inset quasi doublé (top -55%, right -65%, bottom -20%, left -15% — au
lieu de -30%/-35%/-12%/-10%), fondu encore repoussé (28%/88%), flou
60px (au lieu de 55px), opacité 0.45 (au lieu de 0.42).

IMPORTANT — contrairement aux itérations précédentes, ce correctif n'a
PAS pu être vérifié en direct sur le site réel avant d'être committé :
Odoo.sh renvoyait une erreur de plateforme ("Odoo.sh | Platform
Error") sur toutes les tentatives d'accès au moment de ce fix. Les
valeurs ont été estimées par comparaison visuelle des deux captures
fournies par le client, à confirmer une fois le déploiement terminé et
le site de nouveau accessible.
"""
import logging

from odoo import api, SUPERUSER_ID

_logger = logging.getLogger(__name__)


def migrate(cr, version):
    from odoo.addons.capsule_house_theme import run_theme_maintenance

    env = api.Environment(cr, SUPERUSER_ID, {})
    _logger.info(
        "capsule_house_theme: post-migrate 19.0.1.0.29 — halo hero "
        "encore agrandi (inset quasi doublé) pour matcher la taille "
        "du modèle ; NON vérifié en direct cette fois (site "
        "indisponible au moment du fix, Odoo.sh Platform Error)."
    )
    run_theme_maintenance(env)
