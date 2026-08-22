# -*- coding: utf-8 -*-
"""
Rejoue run_theme_maintenance() après une mise à jour du module vers la
version 19.0.1.0.97.

CORRECTIF sur les "petits blocs" gammes/usages de l'accueil, suite à un
retour client avec capture d'écran : le bloc du TITRE de section
apparaissait bien (sélectionnable, panneau Background/Height/
Visibility), mais AUCUNE des 5 cartes n'était sélectionnable
individuellement, et pas de grand bloc englobant le tout non plus.

Cause : en 19.0.1.0.96, le titre était un <section> ENFANT DIRECT de la
zone oe_structure (d'où sa sélection réussie), mais les 5 cartes
restaient nichées 3 niveaux de <div> plus bas (oe_structure >
.ch-gammes-cards-wrap / .ch-usages-cards-wrap > .container >
.ch-gammes-filmstrip / .ch-usages-grid > section.carte). En comparant
avec TOUTES les zones confirmées fonctionnelles ailleurs sur ce site
(pages Aide/Entreprise, /livraison), le point commun identifié : le
panneau Block d'Odoo n'apparaît QUE pour les <section> qui sont des
enfants DIRECTS de la zone oe_structure — jamais pour un <section>
niché sous des <div> intermédiaires, même en l'absence de toute
imbrication <section>-dans-<section>.

Fix : le titre ET chacune des 5 cartes sont maintenant des <section>
FRÈRES DIRECTS de la zone oe_structure elle-même (plus aucun <div>
intermédiaire). La mise en page (grille + centrage type ".container")
est désormais portée directement par la zone oe_structure via une
nouvelle classe (.ch-gammes-zone / .ch-usages-zone, voir pages.css /
homepage.css) : grille CSS (repeat(auto-fit, minmax(...))) qui se
réorganise nativement sur petit écran. Le filmstrip à défilement
horizontal (.ch-gammes-filmstrip) est abandonné pour la variante
accueil ; il reste inchangé et disponible pour /nos-gammes si besoin.

Fichiers modifiés : views/partials/home_gammes.xml,
views/partials/home_usages.xml, static/src/css/pages.css,
static/src/css/homepage.css.
"""
import logging

from odoo import api, SUPERUSER_ID

_logger = logging.getLogger(__name__)


def migrate(cr, version):
    from odoo.addons.capsule_house_theme import run_theme_maintenance

    env = api.Environment(cr, SUPERUSER_ID, {})
    _logger.info(
        "capsule_house_theme: post-migrate 19.0.1.0.97 — titre et "
        "cartes gammes/usages de l'accueil sont maintenant tous des "
        "<section> enfants DIRECTS de la zone oe_structure (plus de "
        "<div> intermédiaire), condition nécessaire (constatée sur "
        "toutes les zones fonctionnelles du site) pour que le panneau "
        "Block Website Builder apparaisse."
    )
    run_theme_maintenance(env)
