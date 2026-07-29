# -*- coding: utf-8 -*-
"""
Rejoue run_theme_maintenance() après une mise à jour du module vers la
version 19.0.1.0.3.

Cette version ne change pas run_theme_maintenance() elle-même : elle
ajoute des <link> CSS directs dans views/templates/layout.xml (voir son
commentaire), un correctif purement XML qui s'applique automatiquement à
chaque mise à jour du module (les vues sont rechargées à chaque -u, sans
dépendre d'un hook Python). Ce dossier est dupliqué ici uniquement par
cohérence avec la règle du README ("à chaque bump de version") — il
rejoue run_theme_maintenance() par sécurité, sans quoi cela n'apporterait
rien de neuf par rapport à 19.0.1.0.2.

Contexte du correctif CSS : diagnostic terrain confirmé — le bundle
compilé web.assets_frontend pour le site Capsule House contient un
@import Google Font mal formé (généré par Odoo, absent de notre code),
qui casse le parsing CSS de tout ce qui suit dans ce bundle partagé,
faisant disparaître nos règles .ch-* (et au passage tout Bootstrap/CSS
natif Odoo pour ce site). Nos 5 fichiers CSS sont désormais aussi chargés
en <link> directs, indépendants de ce bundle et de son bug.
"""
import logging

from odoo import api, SUPERUSER_ID

_logger = logging.getLogger(__name__)


def migrate(cr, version):
    from odoo.addons.capsule_house_theme import run_theme_maintenance

    env = api.Environment(cr, SUPERUSER_ID, {})
    _logger.info(
        "capsule_house_theme: post-migrate 19.0.1.0.3 — rejeu de "
        "run_theme_maintenance() (le correctif principal de cette version "
        "est purement XML, voir views/templates/layout.xml)."
    )
    run_theme_maintenance(env)
