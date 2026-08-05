# -*- coding: utf-8 -*-
"""
Rejoue run_theme_maintenance() après une mise à jour du module vers la
version 19.0.1.0.39.

Client : capture d'écran du backend (vue "Edit" du site builder) montrant
la page décalée horizontalement — menu du haut coupé à gauche ("Home"/
"Tous les pods" invisibles, seuls Studio/Duo/.../Promotions visibles),
titre du hero tronqué ("t pour" au lieu de "fait pour"), scrollbar
horizontale visible en bas de page. Demande : "regarde qu'est-ce qui
cause ce décalage".

Diagnostic en direct (mesure JS sur la page réelle, pas deviné) :
  - document.documentElement.scrollWidth = 1786, clientWidth = 1521 →
    265px de débordement horizontal réel sur TOUTE la page.
  - Recherche de l'élément fautif : masquer temporairement
    `.ch-hero-visual` fait tomber le débordement à 0 (1786 → 1521,
    diff exactement 265px). Confirmé : c'est notre halo décoratif
    (`.ch-hero-visual::before`, voir static/src/css/homepage.css)
    qui est en cause, pas le menu ni un autre composant.

Cause exacte : le halo a des insets très généreux (`left: -90%`,
`right: -75%`), accumulés au fil des itérations v.22 à v.34 pour
matcher visuellement la maquette de référence. `.ch-hero-visual` a
`overflow: visible` posé EXPRÈS pour laisser le halo déborder de sa
propre carte — mais rien, plus haut dans l'arbre (`.ch-hero-grid`,
`.ch-hero`, `body`), ne venait contenir ce débordement au niveau de
la SECTION. Le halo débordait donc de la page ENTIÈRE, ajoutant
265px de largeur scrollable au document — d'où la page décalée/
scrollable horizontalement et le contenu coupé à gauche selon la
position de défilement.

Fix : `overflow: hidden` ajouté sur `.ch-hero` (la section pleine
largeur, pas la carte). Le halo continue de déborder librement à
l'intérieur de la section (visuellement inchangé — toujours visible
par-dessus la colonne de texte, comme voulu), mais ne peut plus
dépasser les bords réels de la page. Testé en direct : scrollWidth
redevenu strictement égal à clientWidth (1521 = 1521) après le fix,
rendu visuel du halo vérifié par capture d'écran (aucune régression).
"""
import logging

from odoo import api, SUPERUSER_ID

_logger = logging.getLogger(__name__)


def migrate(cr, version):
    from odoo.addons.capsule_house_theme import run_theme_maintenance

    env = api.Environment(cr, SUPERUSER_ID, {})
    _logger.info(
        "capsule_house_theme: post-migrate 19.0.1.0.39 — correctif "
        "débordement horizontal de la page (halo .ch-hero-visual::before "
        "non contenu, overflow: hidden ajouté sur .ch-hero)."
    )
    run_theme_maintenance(env)
