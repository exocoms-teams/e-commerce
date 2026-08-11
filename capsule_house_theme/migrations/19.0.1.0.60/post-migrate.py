# -*- coding: utf-8 -*-
"""
Rejoue run_theme_maintenance() après une mise à jour du module vers la
version 19.0.1.0.60.

CAUSE RÉELLE #3 — contenu dynamique dans le hero (analyse complète,
suite au revert de la v59). Comparaison directe, dans la même session
d'édition, entre notre hero (jamais sélectionnable comme bloc) et un
bloc natif Odoo ("Masonry") glissé juste après lui : le bloc natif n'a
LUI NON PLUS aucun data-oe-model sur sa <section> — donc cet attribut
n'a jamais été le déclencheur du panneau Style (toute la piste v49-v56
reposait sur une fausse corrélation).

En comparant précisément le DOM complet fourni par le client :
- Tout ce qui est purement STATIQUE dans le hero est marqué
  `o_editable`/`data-oe-*` par Odoo, y compris des conteneurs entiers
  comme `.ch-hero-visual` (l'illustration).
- `.ch-hero-content`, `.ch-hero-grid` et la `<section>` elle-même ne le
  sont JAMAIS.
- La seule chose commune à ces trois-là (et absente de `.ch-hero-visual`,
  qui lui EST branded) : ils contiennent quelque part `.ch-hero-stats`,
  qui affichait des valeurs dynamiques réelles via `t-esc`
  (published_products_count, units_installed_count) — ainsi que le
  badge de note (rating_value/rating_count) et les cartes flottantes de
  produits vedettes (t-foreach sur featured_products).

Vérification croisée : lecture directe du code source d'exocoms_theme
(hero.xml complet) — AUCUNE expression dynamique nulle part dans leur
hero (juste du texte fixe). Le hero d'avis_hero.xml (qui fonctionne
chez nous aussi) n'en a pas non plus. Confirmé également par la doc
officielle Odoo 19 ("Building blocks > Dynamic Content templates") :
les snippets dynamiques NATIFS d'Odoo (ex: Articles de blog) gardent
leur <section> 100% statique dans l'arch, et injectent le contenu réel
via JavaScript après le chargement de la page — jamais via t-esc/
t-foreach directement dans l'arch.

CORRIGÉ (à la demande du client, "avoir tout ce qu'on veut en pensant
par le JS") : hero.xml (partial_hero_fr/_en) ne contient plus AUCUNE
expression dynamique — plus de t-esc, t-if, t-foreach. Les 4 zones
concernées (badge de note, comptage produits publiés, comptage unités
installées, cartes flottantes + raccourci panier) sont maintenant des
placeholders statiques (masqués par défaut via `d-none` quand la
donnée peut être absente), peuplés côté client par
`static/src/js/main.js` (`initHeroDynamicContent`) à partir d'une
nouvelle route JSON dédiée, `/capsule-house/hero-data.json`
(`CapsuleHouseWebsite.hero_data()`, controllers/main.py) — mêmes
calculs qu'avant (aucune donnée fabriquée), juste injectés après coup
au lieu d'être rendus côté serveur dans l'arch.

Résultat attendu : la <section> du hero redevient 100% statique dans
l'arch source, condition nécessaire (confirmée par comparaison directe
avec exocoms_theme et le bloc natif Masonry) pour qu'Odoo la marque
comme un bloc sélectionnable avec panneau Style complet.
"""
import logging

from odoo import api, SUPERUSER_ID

_logger = logging.getLogger(__name__)


def migrate(cr, version):
    from odoo.addons.capsule_house_theme import run_theme_maintenance

    env = api.Environment(cr, SUPERUSER_ID, {})
    _logger.info(
        "capsule_house_theme: post-migrate 19.0.1.0.60 — contenu dynamique "
        "du hero (note, comptages, produits vedettes) déplacé de t-esc "
        "(arch serveur) vers /capsule-house/hero-data.json + JS "
        "(main.js), pour que la <section> du hero redevienne un bloc "
        "100% statique et sélectionnable dans le Website Builder."
    )
    run_theme_maintenance(env)
