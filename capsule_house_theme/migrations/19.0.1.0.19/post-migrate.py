# -*- coding: utf-8 -*-
"""
Rejoue run_theme_maintenance() après une mise à jour du module vers la
version 19.0.1.0.19.

Corrige l'absence d'indicateur de page active sur "Accueil" (constaté
en conditions réelles : "Studio" s'affiche bien en pastille claire une
fois sur cette catégorie, jamais "Accueil" une fois sur l'accueil).

Cause : le menu "Accueil" pointait vers `/`, qui fait un redirect natif
Odoo vers `website.homepage_url` (= `/capsule-house/home`, posé par
_setup_homepage()). L'URL réellement affichée dans le navigateur une
fois sur l'accueil est donc `/capsule-house/home`, jamais `/` — et le
surlignage natif "page active" du header (#top_menu) compare l'URL du
menu à l'URL réelle de la page, donc ne correspondait jamais pour
Accueil.

Fix : `_setup_menus()` pointe maintenant directement le menu Accueil
vers HOMEPAGE_ROUTE au lieu de `/`. L'ancien menu (url='/') est
automatiquement nettoyé par la logique stray_menus déjà existante (get
remplacé par un nouveau menu à la bonne URL, l'ancien n'étant plus dans
les URLs connues).

Rejeu de run_theme_maintenance() ici pour que l'indicateur "Accueil"
actif s'affiche dès cette mise à jour.
"""
import logging

from odoo import api, SUPERUSER_ID

_logger = logging.getLogger(__name__)


def migrate(cr, version):
    from odoo.addons.capsule_house_theme import run_theme_maintenance

    env = api.Environment(cr, SUPERUSER_ID, {})
    _logger.info(
        "capsule_house_theme: post-migrate 19.0.1.0.19 — menu Accueil "
        "repointé vers HOMEPAGE_ROUTE (corrige l'indicateur de page "
        "active manquant sur Accueil)."
    )
    run_theme_maintenance(env)
