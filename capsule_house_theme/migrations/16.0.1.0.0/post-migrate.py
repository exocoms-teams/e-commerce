# -*- coding: utf-8 -*-
"""
Rejoue run_theme_maintenance() après une mise à jour du module vers la
version 16.0.1.0.0.

IMPORTANT : Odoo ne déclenche `post_init_hook` qu'à l'INSTALLATION initiale
du module, jamais lors d'une simple mise à jour (-u capsule_house_theme).
Sans ce script, un bump de version qui change le comportement du hook
(nouvelle vue à scoper, nouveau produit à publier, etc.) ne serait jamais
rejoué sur une instance déjà installée.

Règle à respecter à CHAQUE bump de version dans __manifest__.py : dupliquer
ce dossier sous `migrations/<nouvelle_version>/post-migrate.py` (même
contenu, il suffit d'appeler run_theme_maintenance). Le cron horaire
(data/cron.xml) sert de filet de sécurité indépendant en complément, pas en
remplacement de ce mécanisme.
"""
import logging

from odoo import api, SUPERUSER_ID

_logger = logging.getLogger(__name__)


def migrate(cr, version):
    from odoo.addons.capsule_house_theme import run_theme_maintenance

    env = api.Environment(cr, SUPERUSER_ID, {})
    _logger.info(
        "capsule_house_theme: post-migrate 16.0.1.0.0 — rejeu de "
        "run_theme_maintenance()."
    )
    run_theme_maintenance(env)
