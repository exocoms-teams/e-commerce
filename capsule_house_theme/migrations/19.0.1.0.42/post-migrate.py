# -*- coding: utf-8 -*-
"""
Rejoue run_theme_maintenance() après une mise à jour du module vers la
version 19.0.1.0.42.

Retour client, deux points, avec capture du menu déroulant du compte
natif : "tu vois ça ne suit pas la langue [My Account / Logout affichés
en anglais malgré le site en français], et va regarder sur
exocoms_theme, j'ai aussi géré l'affichage du header lorsqu'on se
déconnecte, mais les couleurs des pages de connexion et déconnexion
sur exocoms_theme, sur le init, regarde bien, gère bien."

Recherche menée directement dans le code réel d'exocoms_theme (pas
deviné) :

1) Menu compte natif (My Account / Logout) en anglais malgré fr_FR :
   ce dropdown n'est PAS un template à nous, c'est le menu natif du
   module `portal`. exocoms_theme force le rechargement des
   traductions françaises OFFICIELLES d'Odoo pour les modules natifs
   concernés (`mods._update_translations('fr_FR')` sur base, web,
   website, website_sale, portal, auth_signup, mail, sale) — sans quoi
   ces chaînes natives peuvent rester en anglais par défaut sur une
   base mutualisée où le français a été activé après coup. Nouvelle
   fonction `_reload_native_translations(env)`, appelée juste après
   `_setup_languages()` dans run_theme_maintenance.

2) Couleurs des pages de connexion/déconnexion (/web/login et
   assimilées) : exocoms_theme n'a PAS de règle dédiée à ces pages —
   ils ont un unique `.btn-primary` GLOBAL non scopé à un conteneur
   (static/src/css/layout.css), sans !important, qui retombe donc
   naturellement sur toute page native non déjà couverte par une règle
   plus spécifique (dont /web/login). Chez nous, TOUTES les règles
   `.btn-primary` existantes étaient scopées (.oe_website_sale,
   .o_wsale_product_btn, #products_grid, .o_portal_wrap) : aucune ne
   couvrait /web/login, qui restait donc sur le bleu/violet par défaut
   d'Odoo. Ajout d'une règle globale équivalente dans odoo-
   integration.css, avec nos couleurs --ch-terracotta — de par sa
   spécificité CSS plus faible que les règles existantes (déjà plus
   spécifiques et/ou !important), elle ne s'applique que là où rien
   d'autre n'est déjà défini, sans risque de régression ailleurs.
"""
import logging

from odoo import api, SUPERUSER_ID

_logger = logging.getLogger(__name__)


def migrate(cr, version):
    from odoo.addons.capsule_house_theme import run_theme_maintenance

    env = api.Environment(cr, SUPERUSER_ID, {})
    _logger.info(
        "capsule_house_theme: post-migrate 19.0.1.0.42 — traductions "
        "natives fr_FR rechargées (menu compte) + couleur de marque "
        "appliquée globalement aux pages natives (login/signup/reset "
        "password), d'après exocoms_theme."
    )
    run_theme_maintenance(env)
