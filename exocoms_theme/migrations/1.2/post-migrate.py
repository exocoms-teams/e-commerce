# -*- coding: utf-8 -*-
"""
Même mécanisme que migrations/1.1/post-migrate.py (voir ce fichier
pour l'explication complète) : 'post_migrate' n'est pas une clé de
manifest reconnue par Odoo, donc post_migrate_hook() dans __init__.py
n'est JAMAIS rejoué automatiquement par un simple `-u exocoms_theme`
sans ce script de migration versionné.

Ce dossier (1.2) correspond au bump de version fait pour forcer le
rejeu de post_migrate_hook() après l'ajout de
_attach_monetique_attributes_to_products() — sans ce bump, le
rattachement des attributs/filtres Monétique aux produits existants
ne se serait JAMAIS appliqué sur un site déjà installé (seul un site
tout neuf, via post_init_hook, l'aurait eu).

RAPPEL pour la prochaine fois : à chaque nouveau changement dans
post_migrate_hook(), il faut à nouveau :
  1. Monter le numéro de 'version' dans __manifest__.py (ex: 1.2 -> 1.3)
  2. Créer un nouveau dossier migrations/<version>/post-migrate.py
     identique à celui-ci (seul le numéro de dossier compte pour Odoo)
"""
from odoo import api, SUPERUSER_ID


def migrate(cr, version):
    env = api.Environment(cr, SUPERUSER_ID, {})
    from odoo.addons.exocoms_theme import post_migrate_hook
    post_migrate_hook(env)
