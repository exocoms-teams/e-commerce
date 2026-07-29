# -*- coding: utf-8 -*-
"""
Rejoue run_theme_maintenance() après une mise à jour du module vers la
version 19.0.1.0.1.

Cette version ajoute _invalidate_frontend_assets() : elle supprime le/les
ir.attachment du bundle web.assets_frontend de notre site, diagnostiqué
comme compilé une fois de façon incomplète (le <link> réel de la page ne
parsait que les 2 @import Google Fonts, alors qu'une requête brute sur la
même URL renvoyait le fichier complet). Odoo régénère le bundle sous un
nouveau hash au prochain chargement de page — plus besoin de manipulation
manuelle dans Réglages > Technique du backend.

IMPORTANT : Odoo ne déclenche `post_init_hook` qu'à l'INSTALLATION initiale
du module, jamais lors d'une simple mise à jour (-u capsule_house_theme).
Sans ce script, ce correctif ne serait rejoué que par le cron horaire
(data/cron.xml), donc avec jusqu'à 1h de délai — ce script le déclenche
immédiatement à la mise à jour.

Règle à respecter à CHAQUE bump de version dans __manifest__.py : dupliquer
ce dossier sous `migrations/<nouvelle_version>/post-migrate.py` (même
contenu, il suffit d'appeler run_theme_maintenance).

NB : contrairement à post_init_hook (signature `(env)` depuis Odoo 17), les
scripts de migration `migrate(cr, version)` gardent la signature `cr` :
c'est un mécanisme différent (odoo/modules/migration.py), pas affecté par
le changement de signature des hooks pre/post_init.
"""
import logging

from odoo import api, SUPERUSER_ID

_logger = logging.getLogger(__name__)


def migrate(cr, version):
    from odoo.addons.capsule_house_theme import run_theme_maintenance

    env = api.Environment(cr, SUPERUSER_ID, {})
    _logger.info(
        "capsule_house_theme: post-migrate 19.0.1.0.1 — rejeu de "
        "run_theme_maintenance() (inclut l'invalidation du bundle "
        "web.assets_frontend corrompu)."
    )
    run_theme_maintenance(env)
