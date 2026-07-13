# -*- coding: utf-8 -*-
"""
Même mécanisme que migrations/1.3/post-migrate.py (voir ce fichier pour
l'explication complète) : 'post_migrate' n'est pas une clé de manifest
reconnue par Odoo, donc post_migrate_hook() dans __init__.py n'est
JAMAIS rejoué automatiquement par un simple `-u exocoms_theme` sans ce
script de migration versionné.

Ce dossier (1.4) correspond au bump de version fait pour forcer le
rejeu immédiat de post_migrate_hook() après LA vraie correction du bug
des filtres Monétique : _attach_monetique_attributes_to_products()
recherchait les attributs (product.attribute) SANS le contexte de
langue 'fr_FR' utilisé pour les créer dans _setup_monetique_attributes()
-- sur un champ traduisible, ça ne matchait rien, d'où le message de
log "AUCUN attribut trouvé" alors qu'ils existaient bien en base.
Confirmé en conditions réelles sur un environnement de test neuf
(exocoms-e-commerce-exocoms-34808844, install du 2026-07-13).

RAPPEL pour la prochaine fois : à chaque nouveau changement dans
post_migrate_hook(), il faut à nouveau :
  1. Monter le numéro de 'version' dans __manifest__.py (ex: 1.4 -> 1.5)
  2. Créer un nouveau dossier migrations/<version>/post-migrate.py
     identique à celui-ci (seul le numéro de dossier compte pour Odoo)
"""
from odoo import api, SUPERUSER_ID


def migrate(cr, version):
    env = api.Environment(cr, SUPERUSER_ID, {})
    from odoo.addons.exocoms_theme import post_migrate_hook
    post_migrate_hook(env)
