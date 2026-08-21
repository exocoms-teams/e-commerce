# -*- coding: utf-8 -*-
"""
Rejoue run_theme_maintenance() après une mise à jour du module vers la
version 19.0.1.0.85.

Suite de la 19.0.1.0.84 : le client a confirmé que le contenu était bien
éditable après cette version, MAIS le panneau "Block" du Website Builder
(barre d'outils déplacer/dupliquer/supprimer + panneau Background /
Height / Visibility, comme sur exocoms_theme) ne s'affichait pas au
clic — capture d'écran à l'appui comparant exocoms_theme (panneau
visible) et capsule_house_theme (panneau absent, juste "Select a block
on your page to style it.").

Cause : en 19.0.1.0.84, la classe `oe_structure` et le contenu réel
étaient posés sur le MÊME élément `<div>`. Le Website Builder réserve
les options génériques Background/Height/Visibility (et la barre
déplacer/dupliquer/supprimer) aux balises `<section>` — un `<div>`
générique, même marqué `oe_structure`, ne les déclenche pas.

Fix : chaque zone de contenu est restructurée en deux niveaux —
`<div class="oe_structure" id="...">` reste la zone de dépôt (dropzone),
et un `<section>` à l'intérieur porte désormais la classe visuelle
d'origine (ch-aide-content / ch-legal-body / aucune classe pour les
pages Entreprise) et tout le contenu. Le `<section>` est ce qui devient
sélectionnable comme "Block" avec le panneau complet. Le style reste
strictement identique (le div extérieur ne porte plus aucune classe
visuelle, elle a simplement été déplacée sur le section interne).

Vérifié pour chaque fichier : nombre de `<section>` ouvrants = nombre de
`</section>` fermants (2 par page, un par langue FR/EN), plus parsing
XML + compilation Python de l'ensemble du module.

Fichiers modifiés (mêmes 9 pages qu'en 19.0.1.0.84) :
aide_livraison.xml, aide_retours.xml, aide_garantie.xml, aide_faq.xml,
entreprise_apropos.xml, entreprise_concept.xml, mentions_legales.xml,
cgv.xml, confidentialite.xml.
"""
import logging

from odoo import api, SUPERUSER_ID

_logger = logging.getLogger(__name__)


def migrate(cr, version):
    from odoo.addons.capsule_house_theme import run_theme_maintenance

    env = api.Environment(cr, SUPERUSER_ID, {})
    _logger.info(
        "capsule_house_theme: post-migrate 19.0.1.0.85 — le contenu des "
        "9 pages converties en 19.0.1.0.84 est maintenant enveloppé dans "
        "un <section> (au lieu d'un simple <div>) pour que le panneau "
        "Block (Background/Height/Visibility + barre déplacer/dupliquer/"
        "supprimer) du Website Builder s'affiche, comme sur exocoms_theme."
    )
    run_theme_maintenance(env)
