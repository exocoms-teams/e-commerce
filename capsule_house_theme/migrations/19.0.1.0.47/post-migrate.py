# -*- coding: utf-8 -*-
"""
Rejoue run_theme_maintenance() après une mise à jour du module vers la
version 19.0.1.0.47.

Livraison des 2 pages "Entreprise" (À propos, Le concept), liées
depuis la colonne "Entreprise" du footer — brief fourni avec maquette
(contenu, palette --ch-* déjà en place, aucune nouvelle couleur),
construit en code, comme le reste du site :

- views/partials/entreprise_nav.xml : nav en onglets "pills" partagée
  par les 2 pages, état actif calculé dynamiquement depuis l'URL (même
  technique que aide_sidebar.xml / [href$="/shop"], v19.0.1.0.40).
- views/pages/entreprise_apropos.xml : hero (texte + illustration SVG
  reprise à l'identique du hero d'accueil), bandeau 4 statistiques,
  3 cartes "Nos valeurs", historique en timeline verticale.
- views/pages/entreprise_concept.xml : intro, tableau comparatif "Pod
  Capsule House vs Construction traditionnelle" (colonne pod
  surlignée), 4 étapes "De l'atelier à votre terrain", schéma "Coupe
  technique" (même illustration SVG stylisée en contour pointillé).
- controllers/main.py : routes /a-propos, /le-concept (routes neuves,
  pas de garde _is_our_website nécessaire, même logique que /avis et
  les pages Aide).
- static/src/css/pages.css : règles .ch-entreprise-* (nav pills, hero,
  stats, cartes valeurs, historique, tableau comparatif surligné,
  schéma coupe technique) + responsive — réutilise volontairement
  .ch-aide-* (titre, sous-titre, cartes, tableau) plutôt que dupliquer
  un système de classes parallèle.

Contact : conformément à l'instruction explicite du client ("tout les
contact de mes pages doive etre dirigé vers la pages contacts native
odoo"), AUCUNE page de contact n'est construite par ce module. Tous
les liens "Contact" du site (footer, nav Entreprise, bouton "Retours")
pointent vers /contactus, la page de contact NATIVE d'Odoo (module
website, déjà dans les dépendances) — cf. README "Pages Entreprise".

Icônes : FontAwesome, police Inter — même déviation documentée et
justifiée qu'en 19.0.1.0.46 (cohérence avec le reste du site déjà en
production, plutôt que suivre à la lettre un brief qui mentionnait
"Manrope"/icônes SVG en ligne, absents du site réel).
"""
import logging

from odoo import api, SUPERUSER_ID

_logger = logging.getLogger(__name__)


def migrate(cr, version):
    from odoo.addons.capsule_house_theme import run_theme_maintenance

    env = api.Environment(cr, SUPERUSER_ID, {})
    _logger.info(
        "capsule_house_theme: post-migrate 19.0.1.0.47 — pages Entreprise "
        "livrées (À propos, Le concept) ; Contact natif /contactus."
    )
    run_theme_maintenance(env)
