# -*- coding: utf-8 -*-
"""
Rejoue run_theme_maintenance() après une mise à jour du module vers la
version 19.0.1.0.62.

Retour client : le badge de statut du build Odoo.sh affiche "Warning"
au lieu d'un état propre, jugé mal vu côté encadrement. Deux sources de
lignes WARNING identifiées dans les logs du build :

1. "0 failed, 0 error(s) of 0 tests when loading database" — écrite
   par Odoo lui-même (odoo.tests.result), pas par ce module. Odoo logue
   cette ligne de résumé en WARNING systématiquement, que ce soit 0
   test ou tous les tests réussis — comportement générique probablement
   présent sur les 17 sites de la base mutualisée, pas spécifique à
   capsule_house_theme. Non corrigeable depuis ce module.

2. "capsule_house_theme: suppression de N menu(s) par défaut non
   reconnu(s)... ['Contact us']" — celle-ci vient bien de nous
   (_setup_menus, __init__.py). Suppression attendue et idempotente
   (le menu "Contact Us" qu'Odoo crée par défaut sur tout nouveau site,
   jamais dans notre nav définie), pas une anomalie. Passée de
   _logger.warning() à _logger.info().
"""
import logging

from odoo import api, SUPERUSER_ID

_logger = logging.getLogger(__name__)


def migrate(cr, version):
    from odoo.addons.capsule_house_theme import run_theme_maintenance

    env = api.Environment(cr, SUPERUSER_ID, {})
    _logger.info(
        "capsule_house_theme: post-migrate 19.0.1.0.62 — log de "
        "suppression du menu 'Contact us' passé de warning à info "
        "(comportement attendu, pas une anomalie)."
    )
    run_theme_maintenance(env)
