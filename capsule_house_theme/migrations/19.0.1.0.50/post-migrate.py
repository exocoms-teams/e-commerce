# -*- coding: utf-8 -*-
"""
Rejoue run_theme_maintenance() après une mise à jour du module vers la
version 19.0.1.0.50.

SUITE DU CORRECTIF hero / panneau Style (19.0.1.0.49). Après
déploiement de la 19.0.1.0.49, le client a de nouveau montré (capture
d'écran) que le panneau Style du Website Builder restait vide en
cliquant sur le hero de Capsule House, alors que celui d'exocoms
affiche un panneau complet (Layout / Background / Image / Position /
Scroll Effect / Color Filter / Content Width / Height / Visibility) —
`data-snippet` + `data-name` seuls, ajoutés en 19.0.1.0.49, n'ont donc
pas suffi.

Nouvelle comparaison précise des classes de la <section> hero
d'exocoms : `s_exocoms_hero o_colored_level pt32 pb32 oe_img_bg
o_bg_img_center` contre `ch-hero` seul côté Capsule House. Hypothèse
la plus probable : `o_colored_level` est une classe cœur d'Odoo (pas
propre à exocoms) qui enregistre un `<section>` auprès du panneau
d'options générique Background/Layout/Visibility du Website Builder —
exactement l'ensemble d'options visible dans la capture d'écran du
client sur exocoms.

Ajoutée sur `views/partials/hero.xml`
(`<section class="ch-hero o_colored_level" ...>`). IMPORTANT : ceci
reste une hypothèse, pas une certitude vérifiée ligne à ligne dans le
JS cœur d'Odoo (non disponible en local, seuls les deux modules thème
sont mountés) — à confirmer par un nouveau test du client après cette
mise à jour. Si le panneau Style reste vide malgré ce changement, la
prochaine piste à explorer serait `oe_img_bg`/`o_bg_img_center` (liées
à une image de fond, que notre hero n'a pas actuellement — notre fond
est un dégradé CSS, pas une image) ou une différence plus profonde
liée à la façon dont Odoo 19 identifie les zones "éditables" pour le
Website Builder.
"""
import logging

from odoo import api, SUPERUSER_ID

_logger = logging.getLogger(__name__)


def migrate(cr, version):
    from odoo.addons.capsule_house_theme import run_theme_maintenance

    env = api.Environment(cr, SUPERUSER_ID, {})
    _logger.info(
        "capsule_house_theme: post-migrate 19.0.1.0.50 — ajout de "
        "o_colored_level sur la section hero (hypothèse pour faire "
        "apparaître le panneau Style, à confirmer par le client)."
    )
    run_theme_maintenance(env)
