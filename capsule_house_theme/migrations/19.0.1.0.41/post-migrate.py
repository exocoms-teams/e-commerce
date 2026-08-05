# -*- coding: utf-8 -*-
"""
Rejoue run_theme_maintenance() après une mise à jour du module vers la
version 19.0.1.0.41.

Retour client (capture du panneau "Products Design: Chips" dans
l'éditeur de site) : "je t'ai dit que je voulais ce style comme design
sur mes produits du shop, essaye de voir comment ça a été fait sur
exocoms_theme pour bien le faire sur Capsule House."

Root cause : `SHOP_DESIGN_CLASSES` dans __init__.py posait déjà le
design "Chips" via le champ natif `website.shop_opt_products_design_
classes` (bonne mécanique, conforme à la demande explicite du client
d'avoir ça "en code" plutôt qu'un clic dans l'éditeur) — mais la liste
de classes CSS avait été DEVINÉE lors d'une session précédente, pas
vérifiée contre une implémentation réelle. Erreurs trouvées en
comparant au code réel d'exocoms_theme (leur __init__.py, où ce
réglage est écrit deux fois — post_init_hook et le hook de maintenance
principal, donc confirmé fonctionnel en production) :
  - `o_wsale_products_opt_design_thumbs` au lieu de
    `o_wsale_products_opt_design_chips` (la vraie classe "Chips") ;
  - `o_wsale_products_opt_rounded_2` au lieu de `_rounded_4` ;
  - `o_wsale_products_opt_actions_onhover` au lieu de
    `_actions_inline` + `_actions_promote` ;
  - `o_wsale_products_opt_wishlist_fixed` au lieu de
    `_wishlist_inline` ;
  - `o_wsale_products_opt_has_description` et `_actions_subtle`
    présents chez nous mais absents chez exocoms ;
  - `o_wsale_products_opt_has_comparison`, `_cc` et `_thumb_6_5`
    absents chez nous alors que présents chez exocoms.

Fix : `SHOP_DESIGN_CLASSES` remplacée par la liste exacte d'exocoms.
Ajout de `_setup_shop_grid_design()`, filet de sécurité repris de la
même fonction chez exocoms (avec la même prudence de scoping stricte
au website_id — jamais de vue créée ni la vue générique partagée
touchée) : si une vue `website_sale.products` spécifique à notre site
existe déjà, on s'assure que sa classe grid porte bien
`o_wsale_products_opt_design_chips`.
"""
import logging

from odoo import api, SUPERUSER_ID

_logger = logging.getLogger(__name__)


def migrate(cr, version):
    from odoo.addons.capsule_house_theme import run_theme_maintenance

    env = api.Environment(cr, SUPERUSER_ID, {})
    _logger.info(
        "capsule_house_theme: post-migrate 19.0.1.0.41 — SHOP_DESIGN_"
        "CLASSES corrigée avec la vraie liste 'Chips' vérifiée sur "
        "exocoms_theme (la précédente était devinée), + filet de "
        "sécurité _setup_shop_grid_design()."
    )
    run_theme_maintenance(env)
