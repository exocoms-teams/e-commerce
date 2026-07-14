# -*- coding: utf-8 -*-
"""
Même mécanisme que migrations/1.12/post-migrate.py (voir ce fichier
pour l'explication complète) : 'post_migrate' n'est pas une clé de
manifest reconnue par Odoo, donc post_migrate_hook() dans __init__.py
n'est JAMAIS rejoué automatiquement par un simple `-u exocoms_theme`
sans ce script de migration versionné.

Ce dossier (1.13) corrige une ValueError qui faisait planter TOUTE la
mise à jour du module ("Invalid field product.public.category.active"
-- ce modèle n'a PAS de champ 'active' dans cette version d'Odoo,
contrairement à la plupart des modèles) :
  - _merge_stray_categories() (ajoutée en 1.12) l'utilisait dans une
    recherche ET pour archiver une catégorie fantôme.
  - _merge_root_category() (bien plus ancienne, jamais déclenchée en
    conditions réelles jusqu'ici) avait le même bug latent.
Les deux fonctions laissent maintenant simplement la catégorie
concernée en base, vide (tous ses produits déplacés), plutôt que
d'essayer de l'archiver -- sans risque, une catégorie vide n'apparaît
de toute façon jamais dans les filtres boutique.

RAPPEL pour la prochaine fois : à chaque nouveau changement dans
post_migrate_hook(), il faut à nouveau :
  1. Monter le numéro de 'version' dans __manifest__.py (ex: 1.13 -> 1.14)
  2. Créer un nouveau dossier migrations/<version>/post-migrate.py
     identique à celui-ci (seul le numéro de dossier compte pour Odoo)
"""
from odoo import api, SUPERUSER_ID


def migrate(cr, version):
    env = api.Environment(cr, SUPERUSER_ID, {})
    from odoo.addons.exocoms_theme import post_migrate_hook
    post_migrate_hook(env)
