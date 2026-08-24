# -*- coding: utf-8 -*-
"""
Rejoue run_theme_maintenance() après une mise à jour du module vers la
version 19.0.1.0.95.

CORRECTION DE DIAGNOSTIC sur les "petits blocs" gammes/usages de
l'accueil. Une première itération de cette version avait seulement
changé le fond (blanc -> beige) des sections gammes/usages, en pensant
que le seul problème était une zone de fond invisible à cliquer. Retour
client : ce changement ne changeait rien au problème réel (pas de blocs
sélectionnables) et a été ANNULÉ dans la même version, avant d'être
remplacé par le vrai correctif ci-dessous.

Le client réclamait le comportement de la version 19.0.1.0.88 : à
l'époque, chaque carte gammes/usages vivait dans une zone oe_structure
qui la rendait individuellement sélectionnable ("petits blocs"). Ce
comportement avait été perdu en 19.0.1.0.90/.94 (retour à UN SEUL bloc
pour toute la section) après que les tentatives de réintroduction
(19.0.1.0.89, .92 — <section> par carte imbriqué À L'INTÉRIEUR du
<section> englobant) aient été confirmées cassées en test réel.

En relisant la règle Odoo au mot près (Building blocks, Odoo 19) :
"Avoid adding a section tag inside another section tag" — l'interdit
porte sur l'IMBRICATION, pas sur plusieurs <section> FRÈRES à
l'intérieur d'une même zone oe_structure. Ce schéma "frères" est déjà
celui utilisé et confirmé fonctionnel sur les pages Aide/Entreprise
(voir pages.css : ".ch-aide-layout .oe_structure > section + section").
Les tentatives .89/.92 n'avaient jamais testé ce schéma : le <section>
englobant (.ch-gammes-content / .ch-usages) existait TOUJOURS
au-dessus des cartes, donc les cartes-sections étaient réellement
imbriquées, pas frères — d'où l'échec, à raison.

Fix définitif : le <section> englobant est supprimé de
home_gammes.xml/home_usages.xml (remplacé par de simples <div> de mise
en page, jamais des <section>). Titre et chacune des 5 cartes
deviennent des <section> FRÈRES directs à l'intérieur du même
oe_structure — chacun indépendamment déplaçable/supprimable avec son
propre panneau Background/Height/Visibility, comme en 19.0.1.0.88.
Pour les cartes gammes (qui sont des liens), le lien de navigation est
déplacé sur un <a class="ch-gamme-card-link"> en display:contents à
l'intérieur de la section : le padding de la carte reste une zone de
fond cliquable pour sélectionner le bloc, sans empêcher la navigation
au clic sur son contenu visible.

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
        "capsule_house_theme: post-migrate 19.0.1.0.95 — gammes/usages "
        "de l'accueil restructurées en <section> frères (titre + 5 "
        "cartes) dans une même zone oe_structure, au lieu d'un <section> "
        "englobant unique. Restaure le comportement 'petits blocs' de "
        "la 19.0.1.0.88 sans reproduire le bug d'imbrication <section> "
        "dans <section> des versions .89/.92."
    )
    run_theme_maintenance(env)
