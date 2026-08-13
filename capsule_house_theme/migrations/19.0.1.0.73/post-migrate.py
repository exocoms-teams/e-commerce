# -*- coding: utf-8 -*-
"""
Rejoue run_theme_maintenance() après une mise à jour du module vers la
version 19.0.1.0.73.

Retire l'index /nos-gammes (bandeau + filmstrip pleine page, ajouté en
19.0.1.0.71) — demande client explicite après avoir vu le fil d'ariane
réel en production (captures d'écran fournies) : "on doit plus avoir
Home/Our ranges/Capsule mais plutôt Home/Capsule, la page Our ranges ne
doit plus s'afficher".

Cause : depuis la 19.0.1.0.72, le filmstrip des 5 gammes est déjà
affiché directement sur l'accueil (home_gammes.xml) — l'index
/nos-gammes était devenu un doublon pur du même contenu, une fois de
plus la même dynamique que la page "Application" abandonnée plus tôt le
même jour au profit d'une section accueil.

Changements :
- Template `page_nos_gammes` (index) supprimé de nos_gammes.xml.
- Route `/nos-gammes` (controllers/main.py) redirige désormais vers
  '/' au lieu de rendre une page (jamais un 404 — pas de lien cassé
  pour un favori déjà partagé).
- Fil d'ariane de `page_nos_gammes_detail` raccourci : "Accueil / <nom
  de la gamme>" au lieu de "Accueil / Nos gammes / <nom de la gamme>"
  (plus de maillon intermédiaire vers une page qui n'existe plus).
- SCOPED_VIEW_XML_IDS (__init__.py) : entrée
  'capsule_house_theme.page_nos_gammes' retirée (template supprimé).

Les pages détail (/nos-gammes/<slug>) restent inchangées et pleinement
fonctionnelles.
"""
import logging

from odoo import api, SUPERUSER_ID

_logger = logging.getLogger(__name__)


def migrate(cr, version):
    from odoo.addons.capsule_house_theme import run_theme_maintenance

    env = api.Environment(cr, SUPERUSER_ID, {})
    _logger.info(
        "capsule_house_theme: post-migrate 19.0.1.0.73 — index /nos-gammes "
        "retiré (redirige vers '/'), fil d'ariane des pages détail "
        "raccourci en 'Accueil / <gamme>' (plus de maillon 'Nos gammes' "
        "intermédiaire)."
    )
    run_theme_maintenance(env)
