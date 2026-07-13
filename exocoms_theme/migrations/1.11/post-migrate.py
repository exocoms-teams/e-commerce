# -*- coding: utf-8 -*-
"""
Même mécanisme que migrations/1.10/post-migrate.py (voir ce fichier
pour l'explication complète) : 'post_migrate' n'est pas une clé de
manifest reconnue par Odoo, donc post_migrate_hook() dans __init__.py
n'est JAMAIS rejoué automatiquement par un simple `-u exocoms_theme`
sans ce script de migration versionné.

Ce dossier (1.11) corrige un angle mort de _repair_orphaned_categories() :
elle ne matchait un produit orphelin que si le NOM COMPLET d'une
catégorie apparaissait tel quel dans le nom du produit -- ce qui ne
marche presque jamais (ex: 'Chargeurs & Alimentations' n'apparaît
jamais dans "Base chargeur pour TPE Ingenico..."). Ajout d'une liste
de mots-clés PARTIELS (chargeur, housse, protection, coque, câble,
batterie...) -> catégorie cible, à étendre au fur et à mesure des
produits orphelins repérés dans les logs (voir PRODUCT_KEYWORD_CATEGORY
dans __init__.py).

RAPPEL pour la prochaine fois : à chaque nouveau changement dans
post_migrate_hook(), il faut à nouveau :
  1. Monter le numéro de 'version' dans __manifest__.py (ex: 1.11 -> 1.12)
  2. Créer un nouveau dossier migrations/<version>/post-migrate.py
     identique à celui-ci (seul le numéro de dossier compte pour Odoo)
"""
from odoo import api, SUPERUSER_ID


def migrate(cr, version):
    env = api.Environment(cr, SUPERUSER_ID, {})
    from odoo.addons.exocoms_theme import post_migrate_hook
    post_migrate_hook(env)
