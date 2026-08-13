# -*- coding: utf-8 -*-
"""
Rejoue run_theme_maintenance() après une mise à jour du module vers la
version 19.0.1.0.65.

Les pages légales (/mentions-legales, /cgv, /confidentialite, livrées en
19.0.1.0.64) réutilisaient jusque-là les classes .ch-aide-* des pages
Aide (pages.css), faute de style qui leur soit propre. À la demande du
client ("crée un css qui leur est propre et bien propre"), elles ont
maintenant leur propre feuille dédiée :

- static/src/css/legal.css (nouveau fichier) : classes .ch-legal-*
  (breadcrumb, wrap, title, lead, body) — largeur de lecture plus étroite
  (760px) que le reste du site, titres à liseré terracotta, sans
  dépendance aux pages Aide/Entreprise.
- Les 3 templates (mentions_legales.xml, cgv.xml, confidentialite.xml)
  sont mis à jour pour utiliser ces nouvelles classes ; les styles inline
  style="margin-top:32px;" sur chaque <h2> sont retirés (gérés par
  legal.css).
- THEME_ASSETS (__init__.py) étendu avec 'legal.css', enregistré comme
  les autres feuilles du thème via ir.asset scopé website_id (jamais
  dans web.assets_frontend global).

Aucun contenu juridique modifié — uniquement le style/markup.
"""
import logging

from odoo import api, SUPERUSER_ID

_logger = logging.getLogger(__name__)


def migrate(cr, version):
    from odoo.addons.capsule_house_theme import run_theme_maintenance

    env = api.Environment(cr, SUPERUSER_ID, {})
    _logger.info(
        "capsule_house_theme: post-migrate 19.0.1.0.65 — nouvelle feuille "
        "legal.css dédiée aux pages légales (/mentions-legales, /cgv, "
        "/confidentialite), remplace la réutilisation des classes "
        "ch-aide-* des pages Aide."
    )
    run_theme_maintenance(env)
