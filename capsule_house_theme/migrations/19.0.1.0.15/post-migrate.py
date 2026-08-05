# -*- coding: utf-8 -*-
"""
Rejoue run_theme_maintenance() après une mise à jour du module vers la
version 19.0.1.0.15.

Cause EXACTE du 403 sur /shop, confirmée en conditions réelles (session
live inspectée directement) :

    GET /web/session/get_session_info -> uid=2 "Mitchell Admin",
    allowed_companies = {1: "YourCompany"} SEULEMENT.

L'administrateur qui navigue sur le site Capsule House n'a jamais eu
"Exocoms Group" (la société de ce site, créée par _get_company()) dans
ses sociétés autorisées (res.users.company_ids). Dès qu'un code a
besoin de lire un modèle à règle multi-société pendant la navigation
(ici : website_sale.get_pricelist_available() lisant
res.country.group.pricelist_ids), `env.companies` lève
`AccessError("Access to unauthorized or invalid companies.")` — le 403
observé. Ce n'était donc PAS uniquement un problème de pricelist
manquante (le correctif 19.0.1.0.14 restait une bonne pratique, mais
pas la cause du blocage).

Fix : nouvelle fonction `_grant_company_access(env, company)`, appelée
en tout début de `run_theme_maintenance` (juste après `_get_company`),
qui ajoute notre société aux sociétés autorisées de tout utilisateur
membre du groupe Administration/Paramètres (base.group_system).
Idempotent, ne touche jamais un utilisateur non-administrateur ni les
sociétés des autres sites de la base mutualisée.

NB : ce fichier restaure aussi la version du manifeste sur le schéma
19.0.1.0.x — elle avait été repassée à "1.0" localement à un moment (un
retour à ce format court fait sauter silencieusement TOUTES les
migrations au prochain upgrade), voir le commentaire dans
__manifest__.py.
"""
import logging

from odoo import api, SUPERUSER_ID

_logger = logging.getLogger(__name__)


def migrate(cr, version):
    from odoo.addons.capsule_house_theme import run_theme_maintenance

    env = api.Environment(cr, SUPERUSER_ID, {})
    _logger.info(
        "capsule_house_theme: post-migrate 19.0.1.0.15 — société "
        "Exocoms Group ajoutée aux sociétés autorisées des "
        "administrateurs (corrige le 403 'Access to unauthorized or "
        "invalid companies' sur /shop, cause confirmée en conditions "
        "réelles : allowed_companies de l'admin ne contenait que la "
        "société démo par défaut)."
    )
    run_theme_maintenance(env)
