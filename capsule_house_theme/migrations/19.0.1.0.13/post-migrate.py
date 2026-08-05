# -*- coding: utf-8 -*-
"""
Rejoue run_theme_maintenance() après une mise à jour du module vers la
version 19.0.1.0.13.

Retour terrain sur le header natif (19.0.1.0.12) : la nav/pill/icônes
s'affichaient bien restylées, mais deux problèmes restaient visibles :

1. Le site affichait encore le numéro de téléphone factice et le bouton
   "Contact Us" pré-remplis par défaut par Odoo sur tout nouveau site —
   aucune donnée business réelle de Capsule House. Corrigé par CSS
   (layout.css) : masquage par sélecteur structurel
   (li:has(a[href^="tel:"]), li:has(a.btn_cta)), même technique que
   exocoms_theme/header.css.
2. Le logo affichait le placeholder générique Odoo "Your Logo" au lieu
   du nôtre. Cause : `_set_logo()` utilisait `if website.logo: return`
   en supposant ce champ vide par défaut — en réalité Odoo pose lui-même
   un placeholder sur ce champ à la création du site, donc cette
   condition bloquait TOUJOURS la pose de notre logo, dès le premier
   passage du hook. Remplacé par un garde-fou ir.config_parameter
   classique (`capsule_house_theme.logo_applied_v1`, même idiome que
   CONFIG_ASSETS_FIX_KEY) qui force la pose une seule fois, écrasant
   bien le placeholder initial.

Rejeu de run_theme_maintenance() ici pour que _set_logo() applique
effectivement le logo dès cette mise à jour.
"""
import logging

from odoo import api, SUPERUSER_ID

_logger = logging.getLogger(__name__)


def migrate(cr, version):
    from odoo.addons.capsule_house_theme import run_theme_maintenance

    env = api.Environment(cr, SUPERUSER_ID, {})
    _logger.info(
        "capsule_house_theme: post-migrate 19.0.1.0.13 — masquage "
        "téléphone/Contact Us factices + correctif _set_logo() (logo "
        "réellement appliqué, plus bloqué par le placeholder Odoo)."
    )
    run_theme_maintenance(env)
