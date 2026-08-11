# -*- coding: utf-8 -*-
"""
Rejoue run_theme_maintenance() après une mise à jour du module vers la
version 19.0.1.0.59.

REVERT de la v19.0.1.0.58 à la demande explicite du client
("qu'as-tu fait, enlève ça"), sitôt après déploiement — quelque chose
dans le wrapper `<div class="o_editable" contenteditable="true">`
ajouté autour de `<t t-call="capsule_house_theme.partial_hero"/>`
(home.xml) et `<t t-call="capsule_house_theme.avis_hero"/>` (avis.xml)
a visiblement posé un problème en conditions réelles (nature exacte non
encore précisée par le client au moment de ce revert). Retour à l'état
de la v19.0.1.0.57 pour ces deux fichiers : le hero/avis_hero sont de
nouveau t-call-és directement, sans wrapper.

Ne pas retenter cette approche sans comprendre précisément ce qui a
cassé.
"""
import logging

from odoo import api, SUPERUSER_ID

_logger = logging.getLogger(__name__)


def migrate(cr, version):
    from odoo.addons.capsule_house_theme import run_theme_maintenance

    env = api.Environment(cr, SUPERUSER_ID, {})
    _logger.info(
        "capsule_house_theme: post-migrate 19.0.1.0.59 — revert du wrapper "
        "o_editable/contenteditable=true de la v58 sur home.xml/avis.xml, "
        "à la demande du client suite à un problème en conditions réelles."
    )
    run_theme_maintenance(env)
