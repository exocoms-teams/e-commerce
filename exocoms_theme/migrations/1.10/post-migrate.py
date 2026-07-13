# -*- coding: utf-8 -*-
"""
Même mécanisme que migrations/1.9/post-migrate.py (voir ce fichier pour
l'explication complète) : 'post_migrate' n'est pas une clé de manifest
reconnue par Odoo, donc post_migrate_hook() dans __init__.py n'est
JAMAIS rejoué automatiquement par un simple `-u exocoms_theme` sans ce
script de migration versionné.

Ce dossier (1.10) corrige une collision de noms dans
_migrate_products_from_legacy_site() : certains noms de catégorie
existent à PLUSIEURS endroits de notre arborescence (ex: 'Caisse
Enregistreuse' existe à la fois comme grosse catégorie principale ET
comme sous-catégorie de 'Services') -- déjà documenté dans le PDF de
réorganisation ('Ingenico' existe sous 8 branches différentes). Le
matching par nom seul prenait le premier candidat trouvé au hasard,
envoyant potentiellement des produits dans la mauvaise branche tout en
laissant la bonne vide. Corrigé en départageant par le nom du PARENT
côté legacy quand plusieurs candidats existent.

LIMITE CONNUE : ce correctif ne s'applique qu'aux FUTURES migrations
(site neuf / rebuild, ou legacy_products pas encore migrés). Les
produits déjà migrés AVANT ce correctif, qui auraient atterri dans la
mauvaise branche à cause de cette collision, ne sont PAS déplacés
automatiquement -- ils ont déjà quitté le domaine de recherche
(website_id changé). Une vérification manuelle ciblée (ex: comparer le
contenu de 'Caisse Enregistreuse' racine vs 'Services > Caisse
Enregistreuse') reste nécessaire pour ce cas précis.

RAPPEL pour la prochaine fois : à chaque nouveau changement dans
post_migrate_hook(), il faut à nouveau :
  1. Monter le numéro de 'version' dans __manifest__.py (ex: 1.10 -> 1.11)
  2. Créer un nouveau dossier migrations/<version>/post-migrate.py
     identique à celui-ci (seul le numéro de dossier compte pour Odoo)
"""
from odoo import api, SUPERUSER_ID


def migrate(cr, version):
    env = api.Environment(cr, SUPERUSER_ID, {})
    from odoo.addons.exocoms_theme import post_migrate_hook
    post_migrate_hook(env)
