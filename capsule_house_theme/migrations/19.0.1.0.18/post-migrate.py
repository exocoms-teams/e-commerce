# -*- coding: utf-8 -*-
"""
Rejoue run_theme_maintenance() après une mise à jour du module vers la
version 19.0.1.0.18.

CORRECTIF CRITIQUE — la version 19.0.1.0.17 empêchait le module de se
charger DU TOUT (traceback confirmé lors du déploiement) :

    ValueError: Invalid field res.users.groups_id in condition
    ('groups_id', 'in', 4)

Cause : `_grant_company_access()` (ajoutée en 19.0.1.0.15) utilisait
`Users.search([('groups_id', 'in', admin_group.id)])` — le champ
many2many `groups_id` sur `res.users` a été renommé dans Odoo 19.
Corrigé en remplaçant ce domaine fragile par `user.has_group(...)`, la
méthode stable et publique d'Odoo pour tester l'appartenance à un
groupe, indépendante du nom interne du champ m2m sous-jacent (donc plus
robuste aux futurs changements de version aussi).

Rejeu de run_theme_maintenance() ici pour que le module se charge et
s'installe correctement dès cette mise à jour.
"""
import logging

from odoo import api, SUPERUSER_ID

_logger = logging.getLogger(__name__)


def migrate(cr, version):
    from odoo.addons.capsule_house_theme import run_theme_maintenance

    env = api.Environment(cr, SUPERUSER_ID, {})
    _logger.info(
        "capsule_house_theme: post-migrate 19.0.1.0.18 — correctif "
        "critique _grant_company_access() (champ res.users.groups_id "
        "renommé dans Odoo 19, remplacé par has_group())."
    )
    run_theme_maintenance(env)
