# -*- coding: utf-8 -*-
"""
CORRECTIF STRUCTUREL : 'post_migrate' n'est PAS une clé reconnue par
Odoo dans le manifest (seules 'pre_init_hook', 'post_init_hook' et
'uninstall_hook' le sont, confirmé par la documentation officielle
Odoo 15 à 19). Notre fonction post_migrate_hook() dans __init__.py
n'était donc JAMAIS appelée automatiquement par un simple
`-u exocoms_theme` — seule une vraie installation (post_init_hook)
fonctionnait.

Ce fichier utilise le VRAI mécanisme natif Odoo pour exécuter du code
lors d'une mise à jour de module : un script de migration, placé dans
migrations/<version>/post-migrate.py, déclenché automatiquement par
Odoo quand le numéro de version dans __manifest__.py augmente par
rapport à la version actuellement installée en base.

IMPORTANT : pour que ce script se redéclenche à l'avenir (par exemple
après un nouveau changement dans post_migrate_hook), il faut à chaque
fois :
  1. Monter le numéro de 'version' dans __manifest__.py (ex: 1.1 -> 1.2)
  2. Créer/renommer ce dossier migrations/<version>/ pour qu'il
     corresponde exactement à la nouvelle version
"""
from odoo import api, SUPERUSER_ID


def migrate(cr, version):
    env = api.Environment(cr, SUPERUSER_ID, {})
    from odoo.addons.exocoms_theme import post_migrate_hook
    post_migrate_hook(env)