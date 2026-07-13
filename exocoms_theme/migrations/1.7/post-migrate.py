# -*- coding: utf-8 -*-
"""
Même mécanisme que migrations/1.6/post-migrate.py (voir ce fichier pour
l'explication complète) : 'post_migrate' n'est pas une clé de manifest
reconnue par Odoo, donc post_migrate_hook() dans __init__.py n'est
JAMAIS rejoué automatiquement par un simple `-u exocoms_theme` sans ce
script de migration versionné.

Ce dossier (1.7) applique la restriction des filtres Monétique à leur
sous-catégorie pertinente : au lieu de rattacher les 5 attributs
(Forfait DATA compatible, Nombre de chèques par mois, Garantie, Type de
modèle, Quantité) en bloc à tous les produits Monétique, chacun n'est
désormais rattaché qu'aux produits de la sous-catégorie où il a
vraiment du sens (ex: 'Nombre de chèques par mois' uniquement sur les
scanners/lecteurs de chèques sous 'Monnaie & Chèque', pas sur un TPE).
Seul 'Garantie' reste rattaché à toute la gamme. Voir ATTR_SCOPE dans
_attach_monetique_attributes_to_products() (__init__.py).

RAPPEL pour la prochaine fois : à chaque nouveau changement dans
post_migrate_hook(), il faut à nouveau :
  1. Monter le numéro de 'version' dans __manifest__.py (ex: 1.7 -> 1.8)
  2. Créer un nouveau dossier migrations/<version>/post-migrate.py
     identique à celui-ci (seul le numéro de dossier compte pour Odoo)
"""
from odoo import api, SUPERUSER_ID


def migrate(cr, version):
    env = api.Environment(cr, SUPERUSER_ID, {})
    from odoo.addons.exocoms_theme import post_migrate_hook
    post_migrate_hook(env)
