# -*- coding: utf-8 -*-
"""
Rejoue run_theme_maintenance() après une mise à jour du module vers la
version 19.0.1.0.77.

Surfaces des formats de la gamme Capsule (GAMMES_DATA, __init__.py)
passées d'une valeur unique à un intervalle — demande client, après
consultation de /nos-gammes/capsule sur le dev : "pour les différents
formats c'est mieux d'avoir des intervalles en ce qui concerne les
mètres [carrés]".

Studio : 19 m² → 18-20 m². Duo : 28 m² → 26-30 m². Panorama : 38 m² →
36-40 m². Bornes choisies pour englober les vraies valeurs déjà
publiées ailleurs sur le site (Studio 18 m², Panorama jusqu'à 40 m² —
voir aide_faq.xml, réponse chFaq1) plutôt que des chiffres isolés
arbitraires. Le tagline de la gamme Capsule est mis à jour en
conséquence ("18 à 40 m²"). Ces valeurs restent sous le bandeau
'indicative' tant que le fournisseur réel n'est pas confirmé — inchangé
par cette migration.
"""
import logging

from odoo import api, SUPERUSER_ID

_logger = logging.getLogger(__name__)


def migrate(cr, version):
    from odoo.addons.capsule_house_theme import run_theme_maintenance

    env = api.Environment(cr, SUPERUSER_ID, {})
    _logger.info(
        "capsule_house_theme: post-migrate 19.0.1.0.77 — surfaces des "
        "formats Studio/Duo/Panorama (gamme Capsule) passées en intervalle "
        "(18-20 / 26-30 / 36-40 m²) au lieu d'une valeur unique."
    )
    run_theme_maintenance(env)
