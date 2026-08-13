# -*- coding: utf-8 -*-
"""
Rejoue run_theme_maintenance() après une mise à jour du module vers la
version 19.0.1.0.56.

CAUSE TROUVÉE — le client a fourni deux captures DevTools (onglet
Elements) montrant le DOM RENDU réel de son hero sur exocoms_theme
face à celui de Capsule House, ce qui a permis de comparer le rendu
final plutôt que seulement le code source.

Différence identifiée : la <section> hero d'exocoms porte, en plus de
data-snippet/data-name/o_colored_level, les classes `oe_img_bg
o_bg_img_center o_bg_img_origin_border_box` (gestion d'image de
fond). Conséquence directement visible dans le DOM rendu : Odoo
ajoute alors AUTOMATIQUEMENT au rendu, sur la <section> elle-même,
la classe `o_editable` et les attributs `data-oe-model="ir.ui.view"`
`data-oe-id` `data-oe-field="arch"` `data-oe-xpath="/t[1]/section[1]"`.

Sur le hero de Capsule House (jusqu'à la 19.0.1.0.55), ces attributs
n'apparaissaient QUE sur les enfants marqués `oe_editable` (titre,
sous-titre, etc.), jamais sur la `<section>` elle-même — confirmé par
capture DevTools du client. Odoo ne reconnaissait donc la section que
comme un conteneur de texte éditable, pas comme un BLOC sélectionnable
pour le panneau Style. `o_colored_level` seul (ajouté en 19.0.1.0.50)
était insuffisant ; il fallait la combinaison avec `oe_img_bg`/
`o_bg_img_center` pour déclencher ce marquage complet côté Odoo.

Corrigé : `oe_img_bg o_bg_img_center o_bg_img_origin_border_box`
ajoutées à la `<section>` dans `partial_hero_fr`/`partial_hero_en`
(hero.xml) ET `avis_hero_fr`/`avis_hero_en` (avis_hero.xml), pour
cohérence — même diagnostic s'applique probablement au hero de la
page /avis.

Aucune image de fond n'est définie en `style` inline sur ces
sections : rien ne change visuellement, les fonds CSS existants
(dégradé/blanc, déjà dans homepage.css/avis.css) restent inchangés.
Ces classes servent uniquement à déclencher le mécanisme d'édition
d'Odoo. Effet secondaire potentiellement positif : le panneau
Background qui doit maintenant apparaître permettra au client de
remplacer ce fond par une vraie photo directement depuis le Website
Builder s'il le souhaite, sans intervention sur le code.

Cette version est un test empirique bien plus solide que les
précédents (49 à 55) : basé sur une comparaison DIRECTE du DOM rendu
réel des deux sites, pas seulement du code source.
"""
import logging

from odoo import api, SUPERUSER_ID

_logger = logging.getLogger(__name__)


def migrate(cr, version):
    from odoo.addons.capsule_house_theme import run_theme_maintenance

    env = api.Environment(cr, SUPERUSER_ID, {})
    _logger.info(
        "capsule_house_theme: post-migrate 19.0.1.0.56 — oe_img_bg / "
        "o_bg_img_center ajoutées sur les sections hero et avis_hero, "
        "cause identifiée par comparaison directe du DOM rendu "
        "(data-oe-model manquant sur la section elle-même)."
    )
    run_theme_maintenance(env)
