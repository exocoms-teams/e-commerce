# -*- coding: utf-8 -*-
"""
Rejoue run_theme_maintenance() après une mise à jour du module vers la
version 19.0.1.0.94.

CONCLUSION DÉFINITIVE sur l'imbrication de <section> dans <section>
(sections gammes/usages de l'accueil) — obtenue en testant EN DIRECT
sur le site (connexion au back-office via navigateur, mode édition
Website Builder activé, scroll jusqu'à la section "Nos gammes",
clics successifs sur les petites cartes) :

Les cartes en <section class="ch-gamme-card"> / <section
class="ch-usage-card"> (v19.0.1.0.92/.93) affichent bien un contour de
sélection au survol, mais un clic dessus ne remplit JAMAIS le panneau
Style à droite ("Select a block on your page to style it." reste
affiché en permanence), que ce soit sur une carte, sur le titre de la
section, ou ailleurs dans le bloc englobant. La documentation
officielle Odoo 19 (Building blocks) avait donc raison dès le début :
imbriquer un <section> dans un <section> casse la sélection du
Website Builder, INDÉPENDAMMENT du bug de placement de l'oe_structure
corrigé en 19.0.1.0.91 (qui avait pollué le premier test à la .89).

Décision : abandon définitif de l'imbrication. Retour au schéma
19.0.1.0.90 — chaque section (gammes, usages) ne forme qu'UN SEUL bloc
Website Builder (déplaçable, supprimable, panneau Background/Height/
Visibility), avec le texte à l'intérieur éditable au clic, mais sans
possibilité de déplacer/supprimer une carte individuellement. C'est la
limite acceptée pour ce projet sans développement d'un plugin JS
builder_options dédié (hors scope).

Fichiers modifiés : views/partials/home_gammes.xml,
views/partials/home_usages.xml (suppression des <section> imbriqués,
retour à <a>/<div> simples), static/src/css/pages.css
(.ch-gamme-card-link retiré, .ch-gamme-card de nouveau sur le <a>).
"""
import logging

from odoo import api, SUPERUSER_ID

_logger = logging.getLogger(__name__)


def migrate(cr, version):
    from odoo.addons.capsule_house_theme import run_theme_maintenance

    env = api.Environment(cr, SUPERUSER_ID, {})
    _logger.info(
        "capsule_house_theme: post-migrate 19.0.1.0.94 — imbrication "
        "<section> dans <section> abandonnée définitivement (confirmée "
        "cassée en test réel : clic sur une carte ne remplit jamais le "
        "panneau Style). Retour au schéma .90 (un seul bloc par "
        "section, sans sous-blocs)."
    )
    run_theme_maintenance(env)
