# -*- coding: utf-8 -*-
"""
Même mécanisme que migrations/1.5/post-migrate.py (voir ce fichier pour
l'explication complète) : 'post_migrate' n'est pas une clé de manifest
reconnue par Odoo, donc post_migrate_hook() dans __init__.py n'est
JAMAIS rejoué automatiquement par un simple `-u exocoms_theme` sans ce
script de migration versionné.

Ce dossier (1.6) corrige l'erreur "Vous ne pouvez pas modifier le mode
de création des variantes de l'attribut Forfait DATA par TPE, car il
est utilisé sur les produits suivants : Connexions monétiques 4G/5G...".

Cause réelle : l'attribut 'Forfait DATA par TPE' servait DÉJÀ,
légitimement, à générer les 3 vraies variantes de prix (5 Mo/50 Mo/
100 Mo) du produit d'abonnement data "Connexions monétiques 4G/5G...".
Notre fonction voulait réutiliser ce même attribut, sous le même nom,
pour un usage complètement différent : un simple filtre boutique (mode
'no_variant') à afficher sur les produits TPE (Ingenico, Pax...). Odoo
refuse à juste titre de changer le mode d'un attribut déjà utilisé pour
générer de vraies variantes ailleurs.

Corrigé en renommant l'attribut de FILTRE en 'Forfait DATA compatible'
(nom distinct, ne collisionne plus jamais avec l'attribut de variante
réelle 'Forfait DATA par TPE', qui reste inchangé et continue de
fonctionner normalement sur son produit d'origine). Un filet de
sécurité supplémentaire a aussi été ajouté : si un futur nom
d'attribut entre à nouveau en collision avec un attribut déjà utilisé
pour de vraies variantes, la fonction le détecte, l'ignore proprement
(log clair) et continue avec les autres attributs, au lieu de faire
planter toute la mise à jour du module.

RAPPEL pour la prochaine fois : à chaque nouveau changement dans
post_migrate_hook(), il faut à nouveau :
  1. Monter le numéro de 'version' dans __manifest__.py (ex: 1.6 -> 1.7)
  2. Créer un nouveau dossier migrations/<version>/post-migrate.py
     identique à celui-ci (seul le numéro de dossier compte pour Odoo)
"""
from odoo import api, SUPERUSER_ID


def migrate(cr, version):
    env = api.Environment(cr, SUPERUSER_ID, {})
    from odoo.addons.exocoms_theme import post_migrate_hook
    post_migrate_hook(env)
