# -*- coding: utf-8 -*-
"""
Rejoue run_theme_maintenance() après une mise à jour du module vers la
version 19.0.1.0.90.

Le client a testé en direct la tentative de la 19.0.1.0.89 (bloc
englobant + sous-blocs imbriqués sur l'accueil, Gammes/Usages) : ne
fonctionne pas ("j'ai déjà testé, si tu as mis le grand bloc il ne
s'affiche pas sur style"). Recherche menée (WebSearch) sur la
documentation officielle Odoo 19 (Building blocks) pour comprendre la
cause réelle plutôt que continuer à deviner :

"Avoid adding a section tag inside another section tag: this will
trigger twice the Website Builder's options."

Confirmation officielle que la structure tentée en .89 (un <section>
contenant d'autres <section> — le titre et chaque carte) est justement
le cas que la documentation déconseille explicitement. Un vrai système
de blocs imbriqués ("bloc qui contient des blocs") nécessite un plugin
JavaScript dédié (builder_options, so_content_addition_selector,
BuilderAction, enregistré dans le registry website-plugins) — pas
seulement du template QWeb/HTML.

Question posée au client (AskUserQuestion) entre 3 options : bloc
unique pour toute la section, retour aux cartes séparées (déjà
confirmé fonctionnel), ou développement du vrai système imbriqué en
JS. Réponse : "Un seul bloc pour toute la section".

Fix : home_gammes.xml et home_usages.xml reviennent à une structure
SANS section imbriquée — le titre et chaque carte sont de nouveau de
simples <div> (pour les cartes gammes : <a class="ch-gamme-card">
directement, comme avant la 19.0.1.0.87). Seul le <section> racine de
chaque template (déjà enveloppé par l'oe_structure de home.xml depuis
la 19.0.1.0.89, inchangé) reste un bloc Website Builder — UN SEUL bloc
par section, avec le texte à l'intérieur toujours éditable au clic,
mais les cartes ne sont plus déplaçables/supprimables individuellement.

Fichiers modifiés : views/partials/home_gammes.xml (réécrit),
views/partials/home_usages.xml (réécrit), static/src/css/pages.css
(.ch-gamme-card revient sur le <a>, .ch-gamme-card-link supprimée).
"""
import logging

from odoo import api, SUPERUSER_ID

_logger = logging.getLogger(__name__)


def migrate(cr, version):
    from odoo.addons.capsule_house_theme import run_theme_maintenance

    env = api.Environment(cr, SUPERUSER_ID, {})
    _logger.info(
        "capsule_house_theme: post-migrate 19.0.1.0.90 — revert de la "
        "tentative de blocs imbriqués (section dans section, "
        "explicitement déconseillé par la doc Odoo 19). Gammes/Usages "
        "de l'accueil redeviennent UN SEUL bloc Website Builder par "
        "section, sans sous-blocs imbriqués pour les cartes."
    )
    run_theme_maintenance(env)
