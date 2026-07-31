# -*- coding: utf-8 -*-
"""
Rejoue run_theme_maintenance() après une mise à jour du module vers la
version 19.0.1.0.22.

Demande client explicite : "je veux ça [le design 'Chips' de la grille
boutique] mais je veux que ça soit en local" — c'est-à-dire posé par le
code du module, pas par un clic dans l'éditeur de site (Style > Products
Design > Chips), qui ne serait pas versionné ni reproductible sur une
autre instance.

Diagnostic fait en conditions réelles (pas deviné) : ce réglage n'est
PAS une vue à hériter, mais des champs natifs du modèle `website` —
`shop_opt_products_design_classes` (la chaîne de classes CSS qui pilote
le design ; "Chips" correspond en interne à
`o_wsale_products_opt_design_thumbs`), `shop_ppg`/`shop_ppr`/`shop_gap`
(taille de grille), `shop_page_container`, `shop_default_sort`. Valeurs
reprises telles quelles depuis l'état actuellement appliqué sur le
site (lu en direct via JSON-RPC) : 21 produits/page, 3 colonnes, écart
16px, conteneur "regular", tri "En vedette".

Nouvelle fonction `_setup_shop_display(env, website)`, idempotente
(write uniquement si une valeur diffère de celle voulue).

Rejeu de run_theme_maintenance() ici pour que ce réglage soit posé par
le code dès cette mise à jour, même sur une instance où il n'aurait
jamais été configuré manuellement.
"""
import logging

from odoo import api, SUPERUSER_ID

_logger = logging.getLogger(__name__)


def migrate(cr, version):
    from odoo.addons.capsule_house_theme import run_theme_maintenance

    env = api.Environment(cr, SUPERUSER_ID, {})
    _logger.info(
        "capsule_house_theme: post-migrate 19.0.1.0.22 — design boutique "
        "'Chips' posé par le code (_setup_shop_display), plus dépendant "
        "d'un clic dans l'éditeur de site."
    )
    run_theme_maintenance(env)
