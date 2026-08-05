# -*- coding: utf-8 -*-
"""
Rejoue run_theme_maintenance() après une mise à jour du module vers la
version 19.0.1.0.40.

Retour client sur deux captures EN vs FR de la home : "je parle au
niveau de all pods" — en français "Tous les pods" a bien sa pastille
noire pleine (reprise de la maquette), mais en anglais "All pods"
reste en style plat, sans pastille.

Root cause (confirmée en direct en inspectant #top_menu li sur les
deux URLs /capsule-house/home et /en/capsule-house/home) : la pastille
noire vient de static/src/css/layout.css, ciblée par attribut
`.nav-link[href="/shop"]` — une correspondance EXACTE. Mais Odoo
préfixe automatiquement les liens internes avec le code langue quand
ce n'est pas la langue par défaut du site : le lien "Tous les
pods"/"All pods" devient `/en/shop` en anglais (confirmé via
getAttribute('href') sur l'élément réel), qui ne correspond plus à
"/shop" exact. Le style ne s'applique donc qu'en français.

Fix : sélecteur changé en `[href$="/shop"]` (correspondance de
suffixe), qui matche l'URL quel que soit le préfixe de langue
(/shop, /en/shop, /fr/shop...) sans faux positif — aucune autre URL
du menu (/shop/category/X, /shop?promotions=1) ne se termine par
"/shop".
"""
import logging

from odoo import api, SUPERUSER_ID

_logger = logging.getLogger(__name__)


def migrate(cr, version):
    from odoo.addons.capsule_house_theme import run_theme_maintenance

    env = api.Environment(cr, SUPERUSER_ID, {})
    _logger.info(
        "capsule_house_theme: post-migrate 19.0.1.0.40 — correctif "
        "pastille noire 'Tous les pods'/'All pods' absente en anglais "
        "(sélecteur CSS [href=\"/shop\"] exact -> [href$=\"/shop\"] "
        "suffixe, pour survivre au préfixe de langue /en/)."
    )
    run_theme_maintenance(env)
