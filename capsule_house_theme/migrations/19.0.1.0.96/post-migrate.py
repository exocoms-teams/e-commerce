# -*- coding: utf-8 -*-
"""
Rejoue run_theme_maintenance() après une mise à jour du module vers la
version 19.0.1.0.96.

CORRECTIF DÉFINITIF sur les "petits blocs" gammes/usages de l'accueil,
suite à une observation client déterminante : "regarde comment j'ai
fait hero, comment anglais et français sont séparés, ce qui n'empêche
pas son apparition sur edit."

En comparant avec hero.xml (partial_hero_fr / partial_hero_en, deux
templates complets aiguillés par t-call) et aide_livraison.xml (deux
zones oe_structure complètes _content_fr / _content_en, où le t-if
porte sur le <div class="oe_structure"> lui-même) : ces deux fichiers,
CONFIRMÉS fonctionnels en test réel, n'ont JAMAIS de t-if à l'intérieur
d'une zone/section éditable — chaque langue a sa propre zone entière,
strictement dupliquée.

La version 19.0.1.0.95 (restructuration en <section> frères) avait
résolu le problème de nidification <section> dans <section>, mais avait
gardé un défaut différent : une SEULE zone oe_structure partagée entre
FR et EN, avec des t-if épars à l'intérieur des sections (sur les
badges, taglines, CTA). C'est ce schéma "t-if interne à une zone
éditable" — jamais utilisé ailleurs sur ce site — qui est corrigé ici.

Fix : home_gammes.xml et home_usages.xml ont maintenant chacun DEUX
zones oe_structure complètes et indépendantes (id suffixés _fr/_en),
le t-if porte sur le <div class="oe_structure"> lui-même comme sur
/livraison, et tout leur contenu (titre + 5 <section> carte) est écrit
en dur pour cette langue, sans aucun t-if interne. Structure interne
inchangée par ailleurs (toujours des <section> frères, jamais imbriqués
— voir 19.0.1.0.95 pour ce volet du diagnostic).

Fichiers modifiés : views/partials/home_gammes.xml,
views/partials/home_usages.xml.
"""
import logging

from odoo import api, SUPERUSER_ID

_logger = logging.getLogger(__name__)


def migrate(cr, version):
    from odoo.addons.capsule_house_theme import run_theme_maintenance

    env = api.Environment(cr, SUPERUSER_ID, {})
    _logger.info(
        "capsule_house_theme: post-migrate 19.0.1.0.96 — gammes/usages "
        "de l'accueil passées à deux zones oe_structure complètes par "
        "langue (fr/en), sans t-if interne, alignées sur le schéma déjà "
        "confirmé fonctionnel de hero.xml et aide_livraison.xml."
    )
    run_theme_maintenance(env)
