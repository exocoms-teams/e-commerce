# -*- coding: utf-8 -*-
"""
Rejoue run_theme_maintenance() après une mise à jour du module vers la
version 19.0.1.0.76.

Retrait complet de la page /nos-modeles — demande client explicite :
"la page nos modèles doit disparaître sur mon code". Cette page avait
pourtant été conservée à plusieurs reprises pendant toute la refonte de
la taxonomie gammes ("on laisse nos modèles"), mais son contenu
(Studio/Duo/Panorama/Accessoires en cartes plates) est aujourd'hui
entièrement redondant avec la gamme "Capsule" (/nos-gammes/capsule) et
la section gammes de l'accueil (home_gammes.xml, v19.0.1.0.72).

Changements :
- controllers/main.py : nos_modeles() ne rend plus de template, elle
  redirige vers '/' (jamais un 404 pour un lien déjà partagé).
- views/pages/nos_modeles.xml : fichier supprimé.
- __manifest__.py : entrée retirée de la liste `data`.
- __init__.py : entrée 'capsule_house_theme.page_nos_modeles' retirée
  de SCOPED_VIEW_XML_IDS ; constante NOS_MODELES_CATEGORIES retirée
  (plus aucun consommateur).
- static/src/css/pages.css : règles CSS propres à /nos-modeles retirées
  (.ch-models-hero, .ch-models-tags, .ch-models-tag, .ch-models-content,
  .ch-models-grid, .ch-model-card*) ; .ch-models-badge et
  .ch-models-empty CONSERVÉES car toujours utilisées par nos_gammes.xml,
  home_gammes.xml et home_usages.xml.

Odoo lui-même supprimera l'ir.ui.view et le website.page associés à
l'external id 'capsule_house_theme.page_nos_modeles' lors de la mise à
jour du module (comportement natif : une vue dont l'external id
disparaît des fichiers `data` déclarés est retirée à l'upgrade).
"""
import logging

from odoo import api, SUPERUSER_ID

_logger = logging.getLogger(__name__)


def migrate(cr, version):
    from odoo.addons.capsule_house_theme import run_theme_maintenance

    env = api.Environment(cr, SUPERUSER_ID, {})
    _logger.info(
        "capsule_house_theme: post-migrate 19.0.1.0.76 — page /nos-modeles "
        "retirée (redirige vers '/'), template et CSS propres supprimés, "
        "contenu désormais porté par /nos-gammes/capsule et la section "
        "gammes de l'accueil."
    )
    run_theme_maintenance(env)
