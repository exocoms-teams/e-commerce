# -*- coding: utf-8 -*-
"""
Même mécanisme que migrations/1.7/post-migrate.py (voir ce fichier pour
l'explication complète) : 'post_migrate' n'est pas une clé de manifest
reconnue par Odoo, donc post_migrate_hook() dans __init__.py n'est
JAMAIS rejoué automatiquement par un simple `-u exocoms_theme` sans ce
script de migration versionné.

Ce dossier (1.8) corrige un vrai bug de perte de données découvert en
comparant visuellement le site EXOCOMS legacy (référence, tout bien
catégorisé) au nouveau site : dans _migrate_products_from_legacy_site(),
quand le nom d'une catégorie legacy n'avait pas de correspondance
exacte dans notre arborescence (ex: 'Housses et protections' chez
l'ancien site vs 'Housses & protections' chez nous), le code retirait
l'ancienne catégorie du produit SANS RIEN REMETTRE À LA PLACE -- le
produit se retrouvait sans catégorie du tout, invisible dans tous les
filtres boutique (constaté en conditions réelles sur 'Accessoires').

Deux correctifs complémentaires :
  1. _migrate_products_from_legacy_site() normalise maintenant les
     variantes de connecteur (' et ' <-> ' & ') et essaie les catégories
     ANCÊTRES avant d'abandonner -- corrige le problème pour les
     FUTURES migrations (site neuf / rebuild).
  2. Nouvelle fonction _repair_orphaned_categories(), appelée aussi
     dans post_migrate_hook (pas seulement post_init_hook) : rattrape
     les produits DÉJÀ passés sur notre site mais restés sans catégorie
     à cause de ce bug AVANT ce correctif -- indispensable car une fois
     qu'un produit a quitté le site legacy, _migrate_products_from_
     legacy_site() ne le revoit plus jamais lors d'un rejeu.

RAPPEL pour la prochaine fois : à chaque nouveau changement dans
post_migrate_hook(), il faut à nouveau :
  1. Monter le numéro de 'version' dans __manifest__.py (ex: 1.8 -> 1.9)
  2. Créer un nouveau dossier migrations/<version>/post-migrate.py
     identique à celui-ci (seul le numéro de dossier compte pour Odoo)
"""
from odoo import api, SUPERUSER_ID


def migrate(cr, version):
    env = api.Environment(cr, SUPERUSER_ID, {})
    from odoo.addons.exocoms_theme import post_migrate_hook
    post_migrate_hook(env)
