# -*- coding: utf-8 -*-
"""
Rejoue run_theme_maintenance() après une mise à jour du module vers la
version 19.0.1.0.46.

Livraison des 4 pages "Aide" (Livraison, Retours, Garantie, FAQ),
liées depuis la colonne "Aide" du footer (jusque-là en 404, cf.
README) — brief fourni avec maquette (contenu, palette --ch-* déjà en
place, aucune nouvelle couleur), construit en code, comme le reste du
site :

- views/partials/aide_sidebar.xml : menu latéral partagé, état actif
  calculé dynamiquement depuis l'URL (même technique de suffixe que
  [href$="/shop"], v19.0.1.0.40) — jamais codé en dur par page.
- views/pages/aide_livraison.xml, aide_retours.xml, aide_garantie.xml,
  aide_faq.xml : contenu bilingue FR/EN (même convention t-if/t-else
  que le reste du thème). FAQ en accordéon Bootstrap natif (markup du
  snippet Accordéon du Website Builder), pas de JS custom.
- controllers/main.py : routes /livraison, /retours, /garantie, /faq
  (routes neuves, pas de garde _is_our_website nécessaire, même
  logique que /avis).
- static/src/css/pages.css : règles .ch-aide-* + responsive (sidebar
  en barre horizontale scrollable sous 900px).
- static/src/css/variables.css : --ch-red ajoutée (rouge alerte
  #B4553F, distinct du terracotta CTA, absent jusqu'ici).

Icônes : FontAwesome (<i class="fa fa-*">), cohérent avec le reste du
site (hero, avis) — pas d'icônes SVG en ligne dédiées à ces 4 pages
uniquement, ça aurait introduit une incohérence visuelle avec le
reste du thème. Police : Inter (--font-head/--font-body), déjà en
place partout ailleurs sur le site.
"""
import logging

from odoo import api, SUPERUSER_ID

_logger = logging.getLogger(__name__)


def migrate(cr, version):
    from odoo.addons.capsule_house_theme import run_theme_maintenance

    env = api.Environment(cr, SUPERUSER_ID, {})
    _logger.info(
        "capsule_house_theme: post-migrate 19.0.1.0.46 — pages Aide "
        "livrées (Livraison, Retours, Garantie, FAQ)."
    )
    run_theme_maintenance(env)
