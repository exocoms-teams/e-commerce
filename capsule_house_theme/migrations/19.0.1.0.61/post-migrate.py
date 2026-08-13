# -*- coding: utf-8 -*-
"""
Rejoue run_theme_maintenance() après une mise à jour du module vers la
version 19.0.1.0.61.

Retour client après confirmation que le panneau Style fonctionne enfin
sur le hero (v19.0.1.0.60) : le badge de note ("avis en haut") restait
masqué (`d-none`) tant qu'aucun avis n'était publié, comme c'était déjà
le cas avant la v60 (comportement hérité du `t-if="rating_value"`
d'origine). Demande explicite : l'afficher quand même, avec "0", pour
signaler "aucun élément pour le moment" plutôt que de le cacher.

Corrigé : `CapsuleHouseWebsite.hero_data()` (controllers/main.py)
renvoie désormais toujours `rating_value=0`/`rating_message="0 avis"`
(ou "0 reviews") si aucun avis n'est publié, au lieu de `None`. Le JS
(`applyHeroRatingBadge`, main.js) affiche le badge dans tous les cas
(ne teste plus `rating_value` avant de l'afficher). Toujours aucune
donnée fabriquée : "0" est le vrai compte quand il n'y a aucun avis.
"""
import logging

from odoo import api, SUPERUSER_ID

_logger = logging.getLogger(__name__)


def migrate(cr, version):
    from odoo.addons.capsule_house_theme import run_theme_maintenance

    env = api.Environment(cr, SUPERUSER_ID, {})
    _logger.info(
        "capsule_house_theme: post-migrate 19.0.1.0.61 — badge de note du "
        "hero toujours affiché (0 avis si aucun avis publié), au lieu "
        "d'être masqué, à la demande du client."
    )
    run_theme_maintenance(env)
