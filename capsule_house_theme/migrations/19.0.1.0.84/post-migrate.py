# -*- coding: utf-8 -*-
"""
Rejoue run_theme_maintenance() après une mise à jour du module vers la
version 19.0.1.0.84.

Demande client : "à part le header, hero, footer, tout le contenu doit
être à l'intérieur d'un bloc éditable Odoo natif [...] et il doit
s'afficher sur style" — pouvoir modifier le contenu directement depuis
le site (mode édition natif Odoo), sans passer par le code ni par un
déploiement, tout en conservant le rendu visuel actuel.

Convertit en blocs `oe_structure` (mécanisme natif du Website Builder,
déjà utilisé dans ce module pour les placeholders vides "_bottom") les
zones de contenu réellement statique de 9 pages, sur les blocs FR et EN
(18 zones au total) :
- aide_livraison.xml, aide_retours.xml, aide_garantie.xml, aide_faq.xml
  (div .ch-aide-content)
- entreprise_apropos.xml, entreprise_concept.xml (div de contenu, pas
  de classe dédiée auparavant)
- mentions_legales.xml, cgv.xml, confidentialite.xml (div .ch-legal-body)

Seule la classe `oe_structure` et un id unique ont été ajoutés sur les
div existantes — aucun contenu ni classe de style retiré, le rendu
visuel (CSS) est donc strictement identique, seul le contenu devient
éditable en mode Website Builder.

Volontairement EXCLUS de cette conversion (contenu fonctionnel/dynamique
ou explicitement mis de côté par le client) :
- header.xml, footer.xml, hero.xml : exclus explicitement par le client.
- views/pages/nos_gammes.xml et home_gammes.xml/home_usages.xml
  (accueil) : pilotés par GAMMES_DATA/USAGES_DATA (Python), décision
  différée par le client ("on verra celui de gamme entre temps").
- views/pages/shop.xml : patch xpath sur la vue native partagée
  website_sale.products (mutualisée par toute l'instance), son "hero"
  boutique est traité comme le hero de l'accueil.
- views/partials/avis_content.xml : contenu 100% dynamique (avis réels
  en base, formulaire de dépôt, JS de filtrage/notation) — le rendre
  éditable exposerait le formulaire/les scripts à une casse accidentelle
  via le Website Builder, même risque que header/footer.
- aide_sidebar.xml, entreprise_nav.xml : navigation partagée entre
  plusieurs pages, pas du contenu au sens de la demande.

Fichiers modifiés : aide_livraison.xml, aide_retours.xml,
aide_garantie.xml, aide_faq.xml, entreprise_apropos.xml,
entreprise_concept.xml, mentions_legales.xml, cgv.xml,
confidentialite.xml.
"""
import logging

from odoo import api, SUPERUSER_ID

_logger = logging.getLogger(__name__)


def migrate(cr, version):
    from odoo.addons.capsule_house_theme import run_theme_maintenance

    env = api.Environment(cr, SUPERUSER_ID, {})
    _logger.info(
        "capsule_house_theme: post-migrate 19.0.1.0.84 — contenu des "
        "pages Aide/Entreprise/légales converti en blocs oe_structure "
        "éditables nativement depuis le site (Nos Gammes et l'accueil "
        "restent pilotés par GAMMES_DATA/USAGES_DATA, décision différée)."
    )
    run_theme_maintenance(env)
