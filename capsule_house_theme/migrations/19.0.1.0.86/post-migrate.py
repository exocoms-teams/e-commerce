# -*- coding: utf-8 -*-
"""
Rejoue run_theme_maintenance() après une mise à jour du module vers la
version 19.0.1.0.86.

Suite de la 19.0.1.0.85 : le client a précisé que chaque page ne doit
pas être UN SEUL bloc éditable, mais PLUSIEURS blocs distincts,
chacun correspondant à une information différente — "c'est
l'accumulation de ces différents blocs qui forme la page" (même
principe que sur exocoms_theme, où "À propos" n'est qu'un des
nombreux blocs empilés de la page).

Chaque `<section>` unique posée en 19.0.1.0.85 est éclatée en
plusieurs `<section>` sœurs à l'intérieur du même `<div class=
"oe_structure">` (qui reste la zone de dépôt) :
- aide_livraison.xml / aide_retours.xml : intro, encadré, timeline,
  tableau (+ CTA sur retours) → 4 blocs.
- aide_garantie.xml : intro, bandeau garantie, couverture, étapes de
  déclaration → 4 blocs.
- aide_faq.xml : intro, puis un bloc par catégorie de questions
  (Avant l'achat, Commande & paiement, Livraison & installation,
  Garantie & SAV) → 5 blocs. Chaque bloc catégorie garde la classe
  `ch-aide-faq` (sélecteurs CSS `.ch-aide-faq .accordion-*`).
- entreprise_apropos.xml : hero, stats, valeurs, histoire → 4 blocs.
- entreprise_concept.xml : intro+comparatif, comparatif isolé
  (en réalité regroupé avec intro), étapes de fabrication, coupe
  technique → 4 blocs.
- mentions_legales.xml (9), cgv.xml (8), confidentialite.xml (6) :
  un bloc "intro" (titre + chapô) puis un bloc par article numéroté
  (h2), découpage générique sur les frontières de <h2>.

CSS (v19.0.1.0.86) : ajout de `.oe_structure > section + section`
(combinateur de fratrie ADJACENTE, pas générale `~` comme pour les
gammes) dans pages.css (pages Aide/Entreprise, 40px) et legal.css
(pages légales, 32px) pour espacer visuellement les nouveaux blocs
entre eux — un simple <section> n'a par défaut aucune marge, sans
cette règle les blocs se seraient touchés (même symptôme que le bug
:first-of-type déjà rencontré sur /nos-gammes/<slug>, évité ici dès le
départ en choisissant un sélecteur qui ne dépend pas de la position
d'un enfant dans SON propre parent).

Généré par script (views_split_blocks, non conservé dans le module)
utilisant ElementTree pour découper chaque page de façon fiable et
préserver les commentaires XML existants ; validé par re-parsing XML
de l'ensemble du module + comptage open/close des balises <section>
sur les 9 fichiers (doit être pair, un section ouvrante = une
fermante).

Fichiers modifiés : aide_livraison.xml, aide_retours.xml,
aide_garantie.xml, aide_faq.xml, entreprise_apropos.xml,
entreprise_concept.xml, mentions_legales.xml, cgv.xml,
confidentialite.xml, static/src/css/pages.css,
static/src/css/legal.css.
"""
import logging

from odoo import api, SUPERUSER_ID

_logger = logging.getLogger(__name__)


def migrate(cr, version):
    from odoo.addons.capsule_house_theme import run_theme_maintenance

    env = api.Environment(cr, SUPERUSER_ID, {})
    _logger.info(
        "capsule_house_theme: post-migrate 19.0.1.0.86 — les 9 pages "
        "converties en blocs éditables sont maintenant découpées en "
        "plusieurs <section> distinctes (une par information) au lieu "
        "d'un seul bloc par page, avec espacement CSS dédié entre blocs."
    )
    run_theme_maintenance(env)
