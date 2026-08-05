# -*- coding: utf-8 -*-
"""
Rejoue run_theme_maintenance() après une mise à jour du module vers la
version 19.0.1.0.14.

Corrige le 403 constaté en conditions réelles sur /shop ("Tous les
pods") :

    Failed to read field res.country.group.pricelist_ids
    Access to unauthorized or invalid companies.

Cause : `_get_company()` crée la société Exocoms Group via un simple
`res.company.create()`, qui ne seed AUCUNE pricelist par défaut pour
cette société (contrairement à la création d'une société via
l'assistant standard d'Odoo). Sans pricelist scopée à notre company_id,
website_sale élargit sa recherche de pricelist applicable via les
groupes de pays partagés (res.country.group.pricelist_ids) — une liste
qui traverse TOUTES les pricelists de la base mutualisée, y compris
celles des ~16 autres sociétés/sites que la nôtre n'est pas autorisée à
lire (règle d'accès multi-société native d'Odoo) : d'où le 403.

Fix : nouvelle fonction `_setup_pricelist(env, website, company)` qui
crée une pricelist scopée strictement à notre company_id (idempotent,
jamais aucune autre société touchée) et la pose comme pricelist par
défaut du site si le champ existe sur ce modèle/cette version.

Rejeu de run_theme_maintenance() ici pour que /shop redevienne
accessible dès cette mise à jour.
"""
import logging

from odoo import api, SUPERUSER_ID

_logger = logging.getLogger(__name__)


def migrate(cr, version):
    from odoo.addons.capsule_house_theme import run_theme_maintenance

    env = api.Environment(cr, SUPERUSER_ID, {})
    _logger.info(
        "capsule_house_theme: post-migrate 19.0.1.0.14 — création d'une "
        "pricelist scopée à notre société (corrige le 403 sur /shop)."
    )
    run_theme_maintenance(env)
