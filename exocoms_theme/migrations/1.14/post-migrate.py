# -*- coding: utf-8 -*-
"""
Même mécanisme que migrations/1.13/post-migrate.py (voir ce fichier
pour l'explication complète) : 'post_migrate' n'est pas une clé de
manifest reconnue par Odoo, donc post_migrate_hook() dans __init__.py
n'est JAMAIS rejoué automatiquement par un simple `-u exocoms_theme`
sans ce script de migration versionné.

Ce dossier (1.14) corrige _merge_stray_categories() : elle cherchait
les catégories fantômes (comme 'Bases chargeur') avec un filtre strict
website_id = notre site, mais ces catégories, créées par une
manipulation shell antérieure, semblent ne PAS avoir de website_id du
tout (False) -- elles étaient donc invisibles pour la fonction, et la
fusion ne se déclenchait jamais malgré la version 1.13 déployée sans
erreur. Élargi à website_id in [False, notre site] pour la RECHERCHE
DES FANTÔMES uniquement (la catégorie CIBLE reste strictement scopée à
notre site, jamais devinée).

RAPPEL pour la prochaine fois : à chaque nouveau changement dans
post_migrate_hook(), il faut à nouveau :
  1. Monter le numéro de 'version' dans __manifest__.py (ex: 1.14 -> 1.15)
  2. Créer un nouveau dossier migrations/<version>/post-migrate.py
     identique à celui-ci (seul le numéro de dossier compte pour Odoo)
"""
from odoo import api, SUPERUSER_ID


def migrate(cr, version):
    env = api.Environment(cr, SUPERUSER_ID, {})
    from odoo.addons.exocoms_theme import post_migrate_hook
    post_migrate_hook(env)
