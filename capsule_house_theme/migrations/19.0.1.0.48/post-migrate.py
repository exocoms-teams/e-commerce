# -*- coding: utf-8 -*-
"""
Rejoue run_theme_maintenance() après une mise à jour du module vers la
version 19.0.1.0.48.

CORRECTIF STRUCTUREL — blocs non éditables comme sur exocoms_theme.

Question du client : comment le hero d'accueil (et le reste du contenu
de la page d'accueil) est-il protégé pour ne pas être éditable
nativement via le Website Builder, comme c'est le cas sur exocoms_theme ?

Réponse honnête après vérification du code local d'exocoms_theme : ce
n'était PAS le cas jusqu'ici sur capsule_house_theme, et c'est corrigé
par cette version. Les 8 templates de page de ce module
(page_home, avis_page, aide_livraison_page, aide_retours_page,
aide_garantie_page, aide_faq_page, entreprise_apropos_page,
entreprise_concept_page) enveloppaient jusqu'ici TOUT leur contenu réel
dans un même `<div id="wrap" class="oe_structure">`. Deux problèmes
identifiés :

1. `website.layout` (vue native Odoo) pose déjà lui-même un `#wrap` —
   on créait donc un second `id="wrap"` dupliqué (HTML invalide) à
   l'intérieur du premier.
2. `oe_structure` marque toute la zone qu'elle enveloppe comme un
   conteneur de blocs éditable par le Website Builder natif (glisser-
   déposer de blocs, édition inline). En l'appliquant à TOUT le
   contenu (hero, produits vedettes, sidebar Aide, nav Entreprise,
   etc.), on exposait ce contenu à l'édition/suppression accidentelle
   depuis l'interface "Edit" d'Odoo — contraire à la façon dont
   exocoms_theme (module de référence du client) est réellement
   construit.

Vérification directe du code local d'exocoms_theme (views/pages/
home.xml, avis.xml, services.xml) : aucun de ces templates n'enveloppe
son contenu réel dans oe_structure. Les sections (hero, contenu) sont
t-call-ées directement ; seuls des `<div class="oe_structure oe_empty">`
séparés et RÉELLEMENT VIDES sont insérés entre les sections, comme
simples points d'ancrage pour ajouter de nouveaux blocs via le Website
Builder — sans jamais rendre éditable le contenu déjà codé en dur.

Ce module reproduit maintenant exactement le même principe sur ses 8
pages : suppression du `<div id="wrap" class="oe_structure">`
englobant, ajout de placeholders vides (`oe_structure_ch_<page>_
after_hero` / `_bottom`) aux mêmes endroits qu'exocoms_theme (après le
hero sur Accueil et Avis, en bas de page partout). Le hero et tout le
reste du contenu (stats, cartes, tableaux, historique, FAQ, etc.) ne
sont donc plus des zones "oe_structure" et ne sont plus éditables/
supprimables depuis le Website Builder.

Aucun changement visuel : les classes CSS (.ch-home, .ch-aide-page,
etc.) qui étaient posées sur le div supprimé n'étaient ciblées par
aucune règle CSS (vérifié par recherche dans static/src/css/) — leur
suppression n'a aucun impact de rendu.
"""
import logging

from odoo import api, SUPERUSER_ID

_logger = logging.getLogger(__name__)


def migrate(cr, version):
    from odoo.addons.capsule_house_theme import run_theme_maintenance

    env = api.Environment(cr, SUPERUSER_ID, {})
    _logger.info(
        "capsule_house_theme: post-migrate 19.0.1.0.48 — contenu des 8 "
        "pages du module retiré des zones oe_structure (plus éditable "
        "nativement via le Website Builder), comme sur exocoms_theme."
    )
    run_theme_maintenance(env)
