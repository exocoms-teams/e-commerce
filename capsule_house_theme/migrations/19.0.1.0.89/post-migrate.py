# -*- coding: utf-8 -*-
"""
Rejoue run_theme_maintenance() après une mise à jour du module vers la
version 19.0.1.0.89.

Demande client (capture d'écran de la section "Usages" de l'accueil) :
"pourquoi pas des block qui englobe tout ça, avant que à l'intérieur
il y a des block qui contient aussi des block" — un bloc "enveloppe"
pour toute la section (titre + cartes), qui contient lui-même des
blocs indépendants (les cartes), plutôt que des blocs seulement au
même niveau (à plat).

Jusqu'en 19.0.1.0.88, la zone oe_structure entourait uniquement la
grille de cartes (.ch-gammes-filmstrip / .ch-usages-grid) : le
<section> racine de chaque template (ch-gammes-content / ch-usages)
n'était PAS lui-même dans une zone éditable, donc pas sélectionnable
comme "bloc" dans le Website Builder.

Fix : la zone oe_structure est remontée au niveau de home.xml, autour
du <t t-call="..."/> complet. Le <section> entier (titre + grille)
devient ainsi LUI-MÊME un bloc déplaçable/supprimable avec panneau
Background/Height/Visibility, et à l'intérieur, le titre
(.ch-usages-head) et chaque carte (.ch-gamme-card / .ch-usage-card)
restent des <section> individuellement sélectionnables — un bloc qui
englobe des blocs, exactement la structure demandée. Les zones
oe_structure devenues redondantes à l'intérieur de home_gammes.xml et
home_usages.xml ont été retirées (l'oe_structure de home.xml suffit
désormais à rendre éditable tout ce qu'il contient).

Le hero et les produits vedettes restent volontairement HORS
oe_structure (voir note v19.0.1.0.48 dans home.xml) — contenu
fonctionnel, pas concerné par cette demande.

Fichiers modifiés : views/pages/home.xml,
views/partials/home_gammes.xml, views/partials/home_usages.xml.
"""
import logging

from odoo import api, SUPERUSER_ID

_logger = logging.getLogger(__name__)


def migrate(cr, version):
    from odoo.addons.capsule_house_theme import run_theme_maintenance

    env = api.Environment(cr, SUPERUSER_ID, {})
    _logger.info(
        "capsule_house_theme: post-migrate 19.0.1.0.89 — les sections "
        "Gammes et Usages de l'accueil sont maintenant enveloppées "
        "dans un oe_structure au niveau de home.xml : la section "
        "entière devient un bloc, et les cartes qu'elle contient "
        "restent des blocs sélectionnables individuellement."
    )
    run_theme_maintenance(env)
