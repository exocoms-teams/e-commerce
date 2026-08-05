# -*- coding: utf-8 -*-
"""
Rejoue run_theme_maintenance() après une mise à jour du module vers la
version 19.0.1.0.20.

Corrige le placement du titre "All products" sur /shop, constaté en
conditions réelles (capture d'écran comparée à un rendu de référence) :
le titre se retrouvait décalé au lieu de rester aligné à gauche
au-dessus des catégories et de la barre recherche/tri.

Diagnostic confirmé en inspectant le DOM live (pas une supposition) :
`#o_wsale_products_header` est nativement en
`d-flex flex-column gap-2` (titre, puis rangée catégories
`.o_wsale_filmstrip_container`, puis barre recherche/tri
`.products_header.btn-toolbar`, empilés verticalement, alignés à
gauche). Notre CSS (odoo-integration.css) forçait `align-items: center`
et `justify-content: space-between` sur ce même conteneur en colonne —
ce qui recentre chaque ligne horizontalement et perturbe l'espacement
vertical, au lieu de laisser le rendu natif (aligné à gauche) intact.

Fix : `#o_wsale_products_header` ne reçoit plus qu'un padding cosmétique,
plus aucune règle display/flex-direction/align-items/justify-content —
les classes natives suffisent.

Rejeu de run_theme_maintenance() ici uniquement par cohérence avec la
convention du module (un dossier de migration par bump de version) —
ce correctif est pur CSS, aucune donnée à migrer.
"""
import logging

from odoo import api, SUPERUSER_ID

_logger = logging.getLogger(__name__)


def migrate(cr, version):
    from odoo.addons.capsule_house_theme import run_theme_maintenance

    env = api.Environment(cr, SUPERUSER_ID, {})
    _logger.info(
        "capsule_house_theme: post-migrate 19.0.1.0.20 — correctif "
        "placement du titre 'All products' sur /shop (conflit avec "
        "align-items/justify-content sur #o_wsale_products_header, "
        "conteneur natif en flex-column)."
    )
    run_theme_maintenance(env)
