# -*- coding: utf-8 -*-
"""
Même mécanisme que migrations/1.8/post-migrate.py (voir ce fichier pour
l'explication complète) : 'post_migrate' n'est pas une clé de manifest
reconnue par Odoo, donc post_migrate_hook() dans __init__.py n'est
JAMAIS rejoué automatiquement par un simple `-u exocoms_theme` sans ce
script de migration versionné.

Ce dossier (1.9) ajoute un second alias de nom de catégorie découvert
en comparant le site EXOCOMS legacy à notre boutique : 'Bases chargeur'
(ancien site) correspond à 'Chargeurs & Alimentations' (nous) -- ces
deux noms n'ayant rien de commun textuellement, une normalisation de
symboles ('et'/'&') ne suffisait pas, d'où l'ajout d'un dictionnaire
CATEGORY_NAME_ALIASES explicite dans _migrate_products_from_legacy_site()
(__init__.py), à compléter au fur et à mesure que d'autres écarts sont
repérés.

RAPPEL pour la prochaine fois : à chaque nouveau changement dans
post_migrate_hook(), il faut à nouveau :
  1. Monter le numéro de 'version' dans __manifest__.py (ex: 1.9 -> 1.10)
  2. Créer un nouveau dossier migrations/<version>/post-migrate.py
     identique à celui-ci (seul le numéro de dossier compte pour Odoo)
"""
from odoo import api, SUPERUSER_ID


def migrate(cr, version):
    env = api.Environment(cr, SUPERUSER_ID, {})
    from odoo.addons.exocoms_theme import post_migrate_hook
    post_migrate_hook(env)
