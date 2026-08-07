# -*- coding: utf-8 -*-
"""
Rejoue run_theme_maintenance() après une mise à jour du module vers la
version 19.0.1.0.51.

SUITE DU CORRECTIF hero / panneau Style. Après déploiement de la
19.0.1.0.50 (data-snippet + data-name + o_colored_level + oe_editable),
le client a confirmé (module bien mis à niveau à chaque fois, donc pas
un problème de déploiement) que le panneau Style restait toujours vide
sur le hero.

Hypothèse du client, vérifiée dans le code : l'ORGANISATION du
template lui-même, pas seulement ses classes CSS. Avant cette version,
`partial_hero` était UN SEUL template Odoo contenant tout le FR ET
tout le EN à l'intérieur (choisis par t-if/t-else internes) — la
<section data-snippet> n'était donc PAS le résultat direct d'un t-call
vers un template dédié à une seule langue, mais un fragment interne
d'un template plus large gérant aussi le routage de langue.

Vérification du vrai code d'exocoms_theme
(views/partials/hero.xml) : leur hero_section n'est qu'un aiguilleur
de 2 lignes (un t-if par langue) qui t-call soit hero_section_fr soit
hero_section_en — deux templates COMPLETS et INDÉPENDANTS, chacun
avec sa propre <section data-snippet="s_exocoms_hero"> entière, rien
de partagé entre les deux (tout dupliqué, illustration comprise).

Par comparaison, exocoms_theme/views/templates/features.xml (section
non-snippet, pas de data-snippet dessus) utilise lui un simple
t-if/t-else INTERNE à un seul template — confirmant que ce n'est QUE
pour le hero (élément formellement enregistré comme "snippet" via
data-snippet) qu'exocoms scinde en deux templates par langue.

Reproduit à l'identique sur ce module : `views/partials/hero.xml`
scindé en `partial_hero_fr` et `partial_hero_en` (chacun un template
complet et indépendant, illustration + cartes flottantes dupliquées),
`partial_hero` n'est plus qu'un aiguilleur t-if/t-call. Les deux
nouveaux ids sont ajoutés à SCOPED_VIEW_XML_IDS
(_scope_layout_views). `partial_featured_products` (section "Meilleures
ventes", pas de data-snippet) n'est PAS concerné — reste un template
unique avec t-if/t-else interne, comme son équivalent chez exocoms
(features_section).
"""
import logging

from odoo import api, SUPERUSER_ID

_logger = logging.getLogger(__name__)


def migrate(cr, version):
    from odoo.addons.capsule_house_theme import run_theme_maintenance

    env = api.Environment(cr, SUPERUSER_ID, {})
    _logger.info(
        "capsule_house_theme: post-migrate 19.0.1.0.51 — hero d'accueil "
        "scindé en partial_hero_fr / partial_hero_en (templates complets "
        "et indépendants), partial_hero devenu un simple aiguilleur, "
        "comme hero_section/hero_section_fr/hero_section_en chez "
        "exocoms_theme."
    )
    run_theme_maintenance(env)
