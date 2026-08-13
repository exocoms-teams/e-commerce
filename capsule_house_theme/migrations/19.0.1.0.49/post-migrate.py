# -*- coding: utf-8 -*-
"""
Rejoue run_theme_maintenance() après une mise à jour du module vers la
version 19.0.1.0.49.

CORRECTIF — le hero n'apparaissait plus du tout dans le panneau Style
du Website Builder après le correctif structurel de la 19.0.1.0.48
(suppression de l'oe_structure englobant la page). Le client a
signalé, capture d'écran à l'appui, que sur exocoms_theme cliquer sur
le hero fait bien apparaître des options dans l'onglet Style — ce qui
n'était plus le cas côté Capsule House.

Vérification directe du vrai code d'exocoms_theme
(views/partials/hero.xml) : leur hero n'est PAS verrouillé. La
<section> porte `data-snippet="s_exocoms_hero"` et
`data-name="Exocoms Hero"` (ce qui le rend sélectionnable dans le
Website Builder et fait apparaître le panneau Style), et le texte
marketing statique (badge, titre, sous-titre, boutons, bandeau de
confiance) porte la classe `oe_editable` (donc éditable en ligne,
cliquer-taper directement dans le texte). Le SVG décoratif est lui
explicitement marqué `o_not_editable`.

Reproduit à l'identique sur `views/partials/hero.xml` de ce module :
- `data-snippet="s_ch_hero"` + `data-name="Capsule House Hero"` sur la
  <section class="ch-hero"> (les deux blocs de langue FR/EN partagent
  la même section, donc un seul ajout suffit).
- `oe_editable` sur le titre (h1), le sous-titre (p), le bloc des 3
  pastilles et le bandeau de confiance — groupés par bloc, même
  granularité que `s_exocoms_hero_trust oe_editable` /
  `s_exocoms_hero_badge oe_editable` chez exocoms.
- `o_not_editable` ajouté sur le SVG de l'illustration, comme
  `s_exocoms_hero_svg o_not_editable` chez exocoms.

Déviation volontaire et documentée par rapport à exocoms (qui n'a pas
ce problème sur son propre hero) : les 3 statistiques
(ch-hero-stat-number / ch-hero-stat-label) restent NON éditables,
ainsi que le formulaire de recherche, le bouton "Ajouter au panier" et
les cartes produits flottantes. Raison : ces éléments affichent des
valeurs calculées dynamiquement à chaque rendu (t-esc
published_products_count / units_installed_count, données produits
réelles) — les rendre éditables risquerait de figer un chiffre en dur
au premier Save depuis le Website Builder et de casser le comptage/
affichage automatique dès le rendu suivant.
"""
import logging

from odoo import api, SUPERUSER_ID

_logger = logging.getLogger(__name__)


def migrate(cr, version):
    from odoo.addons.capsule_house_theme import run_theme_maintenance

    env = api.Environment(cr, SUPERUSER_ID, {})
    _logger.info(
        "capsule_house_theme: post-migrate 19.0.1.0.49 — hero d'accueil "
        "à nouveau sélectionnable/éditable comme sur exocoms_theme "
        "(data-snippet + oe_editable sur le texte marketing, valeurs "
        "dynamiques protégées)."
    )
    run_theme_maintenance(env)
