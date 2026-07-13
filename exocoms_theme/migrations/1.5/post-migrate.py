# -*- coding: utf-8 -*-
"""
Même mécanisme que migrations/1.4/post-migrate.py (voir ce fichier pour
l'explication complète) : 'post_migrate' n'est pas une clé de manifest
reconnue par Odoo, donc post_migrate_hook() dans __init__.py n'est
JAMAIS rejoué automatiquement par un simple `-u exocoms_theme` sans ce
script de migration versionné.

Ce dossier (1.5) corrige l'erreur "Le nombre de variantes à générer
est supérieur à la limite autorisée" rencontrée juste après le
correctif 1.4 : get_or_create_attribute() dans _setup_monetique_attributes()
ne forçait 'create_variant=no_variant' que sur un attribut CRÉÉ pour la
première fois -- si un attribut du même nom existait déjà en base
partagée (17 sites), potentiellement en mode 'always' par défaut, il
était réutilisé tel quel. Rattacher ensuite cet attribut (mode 'always')
à des dizaines de produits avec toutes ses valeurs provoquait une
explosion combinatoire de variantes. Corrigé en forçant systématiquement
'no_variant', que l'attribut soit nouveau ou réutilisé.

RAPPEL pour la prochaine fois : à chaque nouveau changement dans
post_migrate_hook(), il faut à nouveau :
  1. Monter le numéro de 'version' dans __manifest__.py (ex: 1.5 -> 1.6)
  2. Créer un nouveau dossier migrations/<version>/post-migrate.py
     identique à celui-ci (seul le numéro de dossier compte pour Odoo)
"""
from odoo import api, SUPERUSER_ID


def migrate(cr, version):
    env = api.Environment(cr, SUPERUSER_ID, {})
    from odoo.addons.exocoms_theme import post_migrate_hook
    post_migrate_hook(env)
