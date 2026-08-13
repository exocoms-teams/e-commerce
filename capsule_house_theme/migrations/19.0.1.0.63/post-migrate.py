# -*- coding: utf-8 -*-
"""
Rejoue run_theme_maintenance() après une mise à jour du module vers la
version 19.0.1.0.63.

SEO du site, même principe que exocoms_theme (retour client : "gère
aussi le SEO comme on a fait sur exocoms"). Jusqu'ici, data/seo_data.xml
était vide (juste un commentaire "réservé pour plus tard") : aucune
meta description, robots, Open Graph, Twitter Card ni schema.org
n'existait nulle part dans le module.

Ajouté :
- views/templates/layout.xml : bloc SEO global par défaut (xpath
  //head), même structure que le layout.xml d'exocoms_theme —
  description, robots, Open Graph, Twitter Card, schema.org
  Organization (JSON-LD). Image de partage : le logo du site
  (capsule-house-logo.png). Contenu texte réutilisé tel quel depuis des
  passages déjà validés sur le site (sous-titre du hero notamment),
  jamais inventé.
- Surcharges page par page (t-set="head"), comme exocoms_theme le fait
  pour avis.xml/boutique.xml/services.xml : home.xml, avis.xml,
  aide_livraison.xml, aide_retours.xml, aide_garantie.xml, aide_faq.xml,
  entreprise_apropos.xml, entreprise_concept.xml — description et
  canonical propres à chaque page, dérivés du contenu réel déjà présent
  (h1/sous-titre existants), pas de texte SEO fabriqué.
- Coordonnées schema.org (téléphone, adresse) : reprises à l'identique
  de celles d'exocoms_theme, à la demande explicite du client — Exocoms
  Group est la société qui gère les deux sites. À ajuster si Capsule
  House obtient ses propres coordonnées dédiées.

Non couvert dans cette version : views/pages/shop.xml (page boutique
native website_sale.products) — structure de vue héritée moins
prévisible pour un xpath //head fiable, laissé de côté pour l'instant
plutôt que de risquer un xpath qui casse à l'installation.
"""
import logging

from odoo import api, SUPERUSER_ID

_logger = logging.getLogger(__name__)


def migrate(cr, version):
    from odoo.addons.capsule_house_theme import run_theme_maintenance

    env = api.Environment(cr, SUPERUSER_ID, {})
    _logger.info(
        "capsule_house_theme: post-migrate 19.0.1.0.63 — SEO ajouté "
        "(meta description/robots/OG/Twitter/schema.org global + "
        "surcharges par page), même principe que exocoms_theme."
    )
    run_theme_maintenance(env)
