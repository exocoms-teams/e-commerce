# -*- coding: utf-8 -*-
"""
Rejoue run_theme_maintenance() après une mise à jour du module vers la
version 19.0.1.0.12.

CORRECTIF D'ARCHITECTURE — header natif comme sur exocoms_theme :

Le client a signalé que son propre module de référence (exocoms_theme)
n'a AUCUN template XML custom pour son header en production. Vérification
faite dans exocoms_theme : leur views/templates/header.xml définit bien un
template `custom_header`, mais il n'est jamais t-call-é nulle part — un
reste abandonné. Leur VRAI header est le header NATIF Odoo (header#top),
simplement restylé par CSS (static/src/css/header.css).

Notre module faisait l'inverse : `theme_layout` (layout.xml) remplaçait
entièrement <header id="top"> par notre propre template `theme_header`
(logo/nav/panier/wishlist/recherche/langue/compte tous recodés à la main).
Corrigé dans cette version :

- layout.xml : suppression du xpath position="replace" sur header#top.
  Le header natif reste intact ; seule une fine bannière d'annonce est
  encore insérée position="before" (élément de maquette sans équivalent
  natif, ne touche pas à la structure du header).
- header.xml : ne contient plus que ce bandeau d'annonce
  (theme_announce_bar), tout le reste de l'ancien theme_header a été
  retiré.
- layout.css : nouvelles règles ciblant header#top, .navbar-brand.logo,
  #top_menu, .o_wsale_my_cart, .o_wsale_my_wish,
  .o_header_language_selector, li.dropdown.o_no_autohide_item (mêmes
  cibles que exocoms_theme/header.css), à la place des anciennes règles
  .ch-header/.ch-nav/.ch-icon-link/etc.
- base.css : suppression du padding-top compensant l'ancien header fixe
  (le header natif est en flux normal, comme #wrapwrap chez
  exocoms_theme).
- __init__.py : _set_logo() pointe maintenant vers un vrai fichier
  (static/src/img/capsule-house-logo.png, généré à partir du badge SVG
  validé par le client + wordmark) au lieu du logo.png jamais livré —
  le logo natif (website.logo, affiché par .navbar-brand.logo img)
  s'applique donc réellement maintenant.
- main.js : suppression de initBurger()/initNavActive(), du JS qui
  pilotait notre ancien menu mobile custom (#chBurger/#chNav) —
  remplacé par le comportement natif d'Odoo.
- __manifest__.py : ajout de la dépendance 'website_sale_wishlist' pour
  que l'icône wishlist native soit réellement fonctionnelle.

Rejeu de run_theme_maintenance() ici pour que _set_logo() applique
effectivement le nouveau logo dès la mise à jour.
"""
import logging

from odoo import api, SUPERUSER_ID

_logger = logging.getLogger(__name__)


def migrate(cr, version):
    from odoo.addons.capsule_house_theme import run_theme_maintenance

    env = api.Environment(cr, SUPERUSER_ID, {})
    _logger.info(
        "capsule_house_theme: post-migrate 19.0.1.0.12 — header natif "
        "Odoo restylé par CSS (comme exocoms_theme en production) + "
        "logo réellement appliqué via _set_logo()."
    )
    run_theme_maintenance(env)
