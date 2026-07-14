# -*- coding: utf-8 -*-
"""
Même mécanisme que migrations/1.11/post-migrate.py (voir ce fichier
pour l'explication complète) : 'post_migrate' n'est pas une clé de
manifest reconnue par Odoo, donc post_migrate_hook() dans __init__.py
n'est JAMAIS rejoué automatiquement par un simple `-u exocoms_theme`
sans ce script de migration versionné.

Ce dossier (1.12) corrige une découverte faite en regroupant les
produits "chargeur" par catégorie dans le back-office : ils n'étaient
PAS orphelins (donc invisibles à _repair_orphaned_categories, qui ne
cible que les produits sans AUCUNE catégorie) -- ils étaient déjà
rattachés à une catégorie FANTÔME nommée "Bases chargeur", séparée de
notre "Chargeurs & Alimentations" officielle, probablement créée par
une manipulation shell antérieure à ce module.

Nouvelle fonction _merge_stray_categories() (voir STRAY_CATEGORY_ALIASES
dans __init__.py) : déplace les produits de toute catégorie fantôme
connue vers la bonne catégorie officielle, puis archive la fantôme
(jamais supprimée). Appelée dans post_init_hook ET post_migrate_hook,
comme _repair_orphaned_categories, pour rattraper la production
actuelle sans rebuild.

RAPPEL pour la prochaine fois : à chaque nouveau changement dans
post_migrate_hook(), il faut à nouveau :
  1. Monter le numéro de 'version' dans __manifest__.py (ex: 1.12 -> 1.13)
  2. Créer un nouveau dossier migrations/<version>/post-migrate.py
     identique à celui-ci (seul le numéro de dossier compte pour Odoo)
"""
from odoo import api, SUPERUSER_ID


def migrate(cr, version):
    env = api.Environment(cr, SUPERUSER_ID, {})
    from odoo.addons.exocoms_theme import post_migrate_hook
    post_migrate_hook(env)
