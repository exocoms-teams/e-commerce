# -*- coding: utf-8 -*-
"""
Rejoue run_theme_maintenance() après une mise à jour du module vers la
version 19.0.1.0.105.

RETOUR CLIENT : "pourquoi les produit sur mon carrousel ne me mène nul
par fais exactemnt comme mon carousel sur exocoms" — cliquer sur une
carte produit du carousel "Meilleures ventes" ne menait nulle part.

Cause réelle : views/partials/featured_products.xml construisait les 4
liens de chaque carte (image, nom, bouton "+" FR/EN) avec
`t-attf-href="/shop/#{ item['url'] }"`. Or `item['url']` (=
`product.website_url`, champ Odoo natif calculé, voir
`_serialize_products()` dans controllers/main.py) contient DÉJÀ le
chemin complet ("/shop/nom-du-produit-1"). Le "/shop/" ajouté en dur
dans le template préfixait donc une DEUXIÈME fois, produisant un lien
cassé du type "/shop//shop/nom-du-produit-1" — 404 systématique sur
chaque produit du carousel. Comparaison avec `hero_data()`
(controllers/main.py, plus haut) : cette route utilisait déjà
`item['url']` SANS le re-préfixer, correctement — seule la section
"Meilleures ventes" avait le bug (introduit lors de sa création, jamais
un problème du carousel Bootstrap ajouté en 19.0.1.0.102 lui-même).

Fix : les 4 `t-attf-href="/shop/#{ item['url'] }"` remplacés par
`t-att-href="item['url']"` (pas de "/shop/" en dur). Comportement
désormais identique au carousel "Nouveautés"/"Meilleures ventes"
d'exocoms_theme (dashbord.xml) : chaque carte mène bien vers la vraie
page produit.
"""
import logging

from odoo import api, SUPERUSER_ID

_logger = logging.getLogger(__name__)


def migrate(cr, version):
    from odoo.addons.capsule_house_theme import run_theme_maintenance

    env = api.Environment(cr, SUPERUSER_ID, {})
    _logger.info(
        "capsule_house_theme: post-migrate 19.0.1.0.105 — liens produits "
        "du carousel 'Meilleures ventes' corrigés (item['url'] était "
        "préfixé une 2e fois par '/shop/' en dur, produisant des liens "
        "cassés '/shop//shop/...')."
    )
    run_theme_maintenance(env)
