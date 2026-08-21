# -*- coding: utf-8 -*-
"""
Rejoue run_theme_maintenance() après une mise à jour du module vers la
version 19.0.1.0.95.

CORRECTIF (v19.0.1.0.95) : suite du diagnostic sur "le style des blocs
ne s'affiche pas" (sections "Nos gammes" et "À quoi servira votre pod ?"
de l'accueil). Après confirmation live que le blocage de la .93
(Validation Error footer) et l'imbrication <section> (.92) étaient
résolus, un nouveau test en direct a montré que les éléments individuels
(icônes, liens, titres) sélectionnaient bien leur propre panneau
d'édition — comportement normal — mais que la section elle-même
("Nos gammes"/"usages") ne pouvait pas être sélectionnée comme Block
(panneau Background/Height/Visibility) via un clic sur son fond, alors
que ce mécanisme fonctionne correctement sur /livraison (encart
.ch-aide-callout, fond var(--ch-panel) bien visible).

Cause identifiée : .ch-gammes-home et .ch-usages étaient en fond
var(--ch-white), rigoureusement IDENTIQUE au fond de la page
(body { background: var(--ch-white) }) — aucune zone de fond n'était
donc visuellement distinguable du reste de la page pour repérer où
cliquer, contrairement à /livraison dont l'encart se détache nettement
en beige (var(--ch-panel)).

Fix : fond de .ch-gammes-content.ch-gammes-home (pages.css) et .ch-usages
(homepage.css) passé à var(--ch-panel), padding vertical augmenté, pour
garantir une bande de fond clairement visible et cliquable au-dessus et
en dessous du contenu de chaque section — sur le modèle de ce qui
fonctionne déjà sur /livraison. Aucun changement structurel (pas de
<section> imbriqué, schéma .90/.94 conservé).
"""
import logging

from odoo import api, SUPERUSER_ID

_logger = logging.getLogger(__name__)


def migrate(cr, version):
    from odoo.addons.capsule_house_theme import run_theme_maintenance

    env = api.Environment(cr, SUPERUSER_ID, {})
    _logger.info(
        "capsule_house_theme: post-migrate 19.0.1.0.95 — fond des "
        "sections gammes/usages de l'accueil passé de var(--ch-white) "
        "à var(--ch-panel) pour rendre leur zone de fond visible et "
        "cliquable (sélection Block Website Builder)."
    )
    run_theme_maintenance(env)
