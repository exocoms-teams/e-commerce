# -*- coding: utf-8 -*-
"""
Rejoue run_theme_maintenance() après une mise à jour du module vers la
version 19.0.1.0.78.

Corrige le badge "Disponible" / "Available" affiché sur la gamme
Capsule (page /nos-gammes/capsule et section gammes de l'accueil) —
retour client après consultation du dev : "tu mets disponible alors
que j'ai encore aucun produit dans la boutique".

Le statut interne `GAMME_STATUS_DISPONIBLE` (__init__.py) ne change pas
de valeur (toujours 'disponible'), mais son LIBELLÉ affiché change :
"Disponible" / "Available" → "Détails disponibles" / "Details
available". Objectif : ne plus laisser croire qu'un produit est en
stock/achetable, alors que ces pages sont strictement informatives
(aucune donnée produit réelle derrière pour l'instant) — le badge
signifie seulement que cette gamme a du contenu à montrer (formats,
specs), pas qu'elle est commercialisée.

Fichiers modifiés : views/partials/home_gammes.xml,
views/pages/nos_gammes.xml (template page_nos_gammes_detail).
"""
import logging

from odoo import api, SUPERUSER_ID

_logger = logging.getLogger(__name__)


def migrate(cr, version):
    from odoo.addons.capsule_house_theme import run_theme_maintenance

    env = api.Environment(cr, SUPERUSER_ID, {})
    _logger.info(
        "capsule_house_theme: post-migrate 19.0.1.0.78 — badge de statut "
        "de la gamme Capsule renommé 'Disponible' -> 'Détails disponibles' "
        "(ne doit pas laisser croire à un produit en stock alors que la "
        "boutique n'a encore aucun produit publié sous cette gamme)."
    )
    run_theme_maintenance(env)
