# -*- coding: utf-8 -*-
"""
Rejoue run_theme_maintenance() après une mise à jour du module vers la
version 19.0.1.0.87.

Suite de la 19.0.1.0.86 (client, AskUserQuestion) : "Oui, convertir
maintenant" — la section Nos Gammes/Usages de l'accueil, jusque-là
volontairement laissée de côté (pilotée par GAMMES_DATA/USAGES_DATA en
Python), est convertie en blocs éditables Website Builder, une carte =
un bloc, comme le reste du site.

CHANGEMENT D'ARCHITECTURE ASSUMÉ (accepté explicitement par le client
via la question posée) : les 5 cartes de home_gammes.xml et les 5
cartes de home_usages.xml ne sont plus générées par une boucle
`t-foreach` sur GAMMES_DATA / USAGES_DATA — chacune est maintenant
écrite en dur comme un `<section>` indépendant, avec le contenu copié
depuis les valeurs GAMMES_DATA/USAGES_DATA au moment de la conversion
(statut, icône, tagline, bullets). Conséquence : ces deux sections de
l'accueil et GAMMES_DATA/USAGES_DATA peuvent désormais diverger si
l'un est modifié sans l'autre. GAMMES_DATA/USAGES_DATA restent
utilisées ailleurs sans changement : /nos-gammes/<slug> (page détail
complète par gamme) continue d'utiliser GAMMES_DATA normalement, ce
n'est QUE le résumé affiché en filmstrip sur l'accueil qui est
maintenant statique/éditable.

Détail technique (home_gammes.xml) : `.ch-gamme-card` était posée sur
le `<a>` (lien cliquable) pour bénéficier de `flex: 0 0 220px` en
enfant direct de `.ch-gammes-filmstrip` (display:flex). Le panneau
Block du Website Builder n'existant que sur les `<section>`, la classe
`.ch-gamme-card` est déplacée sur un `<section>` wrapper (nouvel enfant
direct du filmstrip), et le `<a class="ch-gamme-card-link">` passe en
`display: contents` (pages.css) : il disparaît de la mise en page (le
flex-basis s'applique donc bien au section) tout en restant cliquable
sur toute la carte, car ses enfants restent dans le DOM à l'intérieur
du lien.

Aucune règle d'espacement supplémentaire nécessaire ici (contrairement
aux pages Aide/Entreprise/légales en 19.0.1.0.86) : .ch-gammes-filmstrip
et .ch-usages-grid utilisaient déjà `gap` (flex/grid), qui fonctionne
identiquement quel que soit le tag des enfants directs.

Fichiers modifiés : views/partials/home_gammes.xml (réécrit),
views/partials/home_usages.xml (réécrit), static/src/css/pages.css
(.ch-gamme-card déplacée sur section, .ch-gamme-card-link ajoutée).
"""
import logging

from odoo import api, SUPERUSER_ID

_logger = logging.getLogger(__name__)


def migrate(cr, version):
    from odoo.addons.capsule_house_theme import run_theme_maintenance

    env = api.Environment(cr, SUPERUSER_ID, {})
    _logger.info(
        "capsule_house_theme: post-migrate 19.0.1.0.87 — les sections "
        "Nos Gammes et Usages de l'accueil sont converties en blocs "
        "éditables individuels (une carte = un bloc), au lieu d'être "
        "générées par boucle depuis GAMMES_DATA/USAGES_DATA."
    )
    run_theme_maintenance(env)
