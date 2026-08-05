# -*- coding: utf-8 -*-
"""
Rejoue run_theme_maintenance() après une mise à jour du module vers la
version 19.0.1.0.10.

Correctif purement XML/CSS (header.xml + layout.css), inspiré du même
ensemble d'icônes que exocoms_theme (panier, wishlist, recherche,
sélecteur de langue, compte client) :

- Réordonné les icônes existantes : panier, wishlist, recherche.
- Ajouté un sélecteur de langue natif (request.website.language_ids +
  route native /website/lang/<url_code>), masqué automatiquement s'il
  n'y a qu'une seule langue active sur le site.
- Ajouté un menu compte client : lien "Connexion" pour un visiteur
  public, menu "Mon compte" / "Déconnexion" pour un utilisateur identifié
  (même schéma que exo-profile-dropdown dans exocoms_theme).

Aucun changement de logique Python : ce correctif s'applique
automatiquement au rechargement des vues.
"""
import logging

from odoo import api, SUPERUSER_ID

_logger = logging.getLogger(__name__)


def migrate(cr, version):
    from odoo.addons.capsule_house_theme import run_theme_maintenance

    env = api.Environment(cr, SUPERUSER_ID, {})
    _logger.info(
        "capsule_house_theme: post-migrate 19.0.1.0.10 — rejeu de "
        "run_theme_maintenance() (sélecteur de langue + menu compte dans "
        "le header)."
    )
    run_theme_maintenance(env)
