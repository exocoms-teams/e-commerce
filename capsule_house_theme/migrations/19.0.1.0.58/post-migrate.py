# -*- coding: utf-8 -*-
"""
Rejoue run_theme_maintenance() après une mise à jour du module vers la
version 19.0.1.0.58.

PREUVE DÉCISIVE (comparaison directe, même session d'édition, même
page) : le client a glissé un bloc NATIF Odoo ("Masonry") juste après
le hero de l'accueil et cliqué dessus — le panneau Style s'est affiché
normalement (Layout/Background/Content Width/Height/Visibility). Clic
sur le hero juste au-dessus : toujours rien. Capture DevTools du code
du bloc natif fournie par le client :

    <section class="s_masonry_block ..." data-snippet="s_masonry_block"
             data-name="Masonry" contenteditable="false">

AUCUN data-oe-model/data-oe-id/data-oe-xpath sur cette <section> non
plus ! Toute la piste suivie depuis la v56 (ajouter oe_img_bg etc. pour
faire apparaître data-oe-model sur la section) reposait donc sur une
fausse corrélation — l'attribut n'est pas ce qui déclenche le panneau
Style.

La vraie différence, visible dans le même DOM : le bloc Masonry est un
ENFANT de <div id="oe_structure_ch_home_after_hero" class="oe_structure
oe_empty o_editable" contenteditable="true">. Notre hero, lui, n'a AUCUN
ancêtre portant la classe `o_editable` ni `contenteditable="true"`
jusqu'à <main> inclus (confirmé par lecture directe du DOM rendu). Le
SnippetsMenu d'Odoo cherche, au clic, le plus proche ancêtre marqué
comme zone éditable (`o_editable` + `contenteditable="true"`) pour
savoir si l'élément cliqué (ou son ancêtre `[data-snippet]`) est
sélectionnable — sans cet ancêtre, aucun clic ne peut jamais activer
la sélection de bloc, quel que soit le balisage du hero lui-même. Ça
explique pourquoi 8 tentatives successives sur le balisage du hero
(v49-v56) n'ont rien changé : le vrai problème était un niveau
au-dessus, dans page_home.xml/avis.xml, pas dans hero.xml/avis_hero.xml.

Corrigé : le `<t t-call="capsule_house_theme.partial_hero"/>` (et
`avis_hero`) est maintenant enveloppé dans un `<div class="o_editable"
contenteditable="true">` simple — PAS un `oe_structure` (qui
redéclencherait le bug de la v48 : Odoo strip data-oe-model sur le
contenu atteint via <t t-call> à l'intérieur d'un oe_structure), juste
les classes/attributs minimaux qui rendent la zone visible au
SnippetsMenu. La <section> elle-même garde contenteditable="false",
donc aucun risque de taper du texte libre dans ce nouveau wrapper.
"""
import logging

from odoo import api, SUPERUSER_ID

_logger = logging.getLogger(__name__)


def migrate(cr, version):
    from odoo.addons.capsule_house_theme import run_theme_maintenance

    env = api.Environment(cr, SUPERUSER_ID, {})
    _logger.info(
        "capsule_house_theme: post-migrate 19.0.1.0.58 — hero/avis_hero "
        "enveloppés dans un wrapper o_editable/contenteditable=true "
        "(page_home.xml, avis.xml), cause identifiée par comparaison "
        "directe avec un bloc natif Odoo dans la même session d'édition."
    )
    run_theme_maintenance(env)
