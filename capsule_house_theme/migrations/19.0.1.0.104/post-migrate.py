# -*- coding: utf-8 -*-
"""
Rejoue run_theme_maintenance() après une mise à jour du module vers la
version 19.0.1.0.104.

CORRECTIF CRITIQUE — la 19.0.1.0.103 (bouton "Voir dans la boutique" du
hero de gamme) empêchait le module de se charger DU TOUT en production :

    ImportError: cannot import name 'slug' from
    'odoo.addons.http_routing.models.ir_http'
    (/home/odoo/src/odoo/addons/http_routing/models/ir_http.py)

Log complet fourni par le client : "Couldn't load module
capsule_house_theme" / "Failed to load registry" / "Failed to
initialize database" — la base entière refusait de démarrer tant que ce
module (106/107 au chargement) plantait à l'import.

Cause réelle : en Odoo 19, la fonction `slug()` a été déplacée hors de
`odoo.addons.http_routing.models.ir_http` (import direct au niveau
module, qui existait encore en Odoo 17/18) vers une MÉTHODE du modèle
`ir.http` : `request.env['ir.http']._slug(record)`. L'ancien import
top-level n'existe simplement plus dans le code source d'Odoo 19.

Fix : controllers/main.py n'importe plus `slug` — nos_gammes_detail()
appelle désormais `request.env['ir.http']._slug(category)` directement,
là où l'URL de la catégorie boutique est construite. Comportement
fonctionnel inchangé (le bouton "Voir dans la boutique" ajouté en
19.0.1.0.103 fonctionne maintenant comme prévu), seule la méthode
d'obtention du slug était fautive.
"""
import logging

from odoo import api, SUPERUSER_ID

_logger = logging.getLogger(__name__)


def migrate(cr, version):
    from odoo.addons.capsule_house_theme import run_theme_maintenance

    env = api.Environment(cr, SUPERUSER_ID, {})
    _logger.info(
        "capsule_house_theme: post-migrate 19.0.1.0.104 — correctif "
        "critique : import 'slug' invalide en Odoo 19 (empêchait le "
        "chargement du module) remplacé par "
        "request.env['ir.http']._slug(record)."
    )
    run_theme_maintenance(env)
