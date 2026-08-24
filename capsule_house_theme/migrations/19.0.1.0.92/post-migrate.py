# -*- coding: utf-8 -*-
"""
Rejoue run_theme_maintenance() après une mise à jour du module vers la
version 19.0.1.0.92.

Contexte : à la 19.0.1.0.89, une première tentative de "grand bloc
Website Builder contenant des petits blocks" (section imbriquée dans
section) avait été testée EN MÊME TEMPS qu'un bug de placement de
l'oe_structure (oe_structure dans home.xml, reliée par t-call à une
vue tierce). Le test client ("rien ne s'affiche sur style") ne
permettait donc pas de savoir laquelle des deux causes était en jeu.

Le bug de placement a été isolé et corrigé en 19.0.1.0.91
(oe_structure redescendu dans le même fichier que le <section> qu'il
rend éditable). Cette version réintroduit SEULE l'imbrication de
<section> (home_gammes.xml : chaque carte gamme redevient un
<section class="ch-gamme-card"> avec un <a class="ch-gamme-card-link">
en display:contents à l'intérieur ; home_usages.xml : chaque carte
usage redevient un <section class="ch-usage-card">), pour obtenir une
mesure propre de ce que fait réellement Odoo sur ce point précis.

Rappel : la documentation officielle Odoo 19 (Building blocks)
déconseille cette imbrication en soi ("this will trigger twice the
Website Builder's options"), indépendamment du bug .91. Il est donc
possible que le résultat en test réel montre un panneau d'options
dupliqué/incohérent sur les petites cartes même une fois le bug de
placement écarté — auquel cas revenir à l'option "un seul bloc pour
toute la section" (schéma 19.0.1.0.90).

Le filet de sécurité _reset_customized_views() (RESETTABLE_VIEW_XML_IDS
dans __init__.py, déjà en place depuis la 19.0.1.0.91) couvre toujours
capsule_house_theme.partial_home_gammes et .partial_home_usages —
utile si une des versions intermédiaires cassées avait été sauvegardée
en base entre-temps.

Fichiers modifiés : views/partials/home_gammes.xml,
views/partials/home_usages.xml, static/src/css/pages.css.

NB : au moment de cette version, une Validation Error bloque encore la
mise à jour du module en base client (`xpath expr="//div[@id='footer']"`
introuvable) — sans rapport avec ce module (aucune occurrence de cet
xpath dans son code), probablement une personnalisation Website Builder
scopée au site, stockée uniquement en base. À résoudre séparément avant
de pouvoir vérifier cette version en conditions réelles.
"""
import logging

from odoo import api, SUPERUSER_ID

_logger = logging.getLogger(__name__)


def migrate(cr, version):
    from odoo.addons.capsule_house_theme import run_theme_maintenance

    env = api.Environment(cr, SUPERUSER_ID, {})
    _logger.info(
        "capsule_house_theme: post-migrate 19.0.1.0.92 — imbrication "
        "<section> dans <section> réintroduite seule (bug de placement "
        "de l'oe_structure déjà corrigé en .91), pour mesurer proprement "
        "si le Website Builder l'accepte malgré la mise en garde de la "
        "documentation officielle."
    )
    run_theme_maintenance(env)
