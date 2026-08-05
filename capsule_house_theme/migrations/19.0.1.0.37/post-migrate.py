# -*- coding: utf-8 -*-
"""
Rejoue run_theme_maintenance() après une mise à jour du module vers la
version 19.0.1.0.37.

Retour client sur la v.36 (captures FR vs EN à l'appui) : "en plus le
live chat ne s'affiche pas et regarde le header en anglais, c'est pas
pareil que celui en français et en plus il n'est pas traduit, et en
plus la partie meilleures ventes lui aussi n'est pas traduit — je t'ai
demandé de tout gérer". La v.36 avait traduit hero/footer/avis mais
oublié plusieurs endroits :

1) Menu du haut (Accueil, Tous les pods, Promotions, Avis clients,
   Accessoires) : `website.menu.name` est traduisible nativement dans
   Odoo, mais aucune valeur n'avait jamais été posée pour en_US —
   `_setup_menus()` pose maintenant une traduction anglaise via
   `record.with_context(lang='en_US').write({'name': ...})` pour les
   libellés d'UI. Studio/Duo/Panorama restent inchangés (noms de
   gamme, pas du texte d'interface — comme les noms de produits ne
   sont jamais traduits ailleurs dans ce module).
2) `views/partials/featured_products.xml` ("Meilleures ventes") :
   entièrement oubliée en v.36, ajoutée ici (titre, lien "Voir tous
   les modèles", message d'attente, titre du bouton produit).
3) `views/templates/header.xml` (bandeau d'annonce) : oublié aussi.
4) `views/pages/shop.xml` (titre/sous-titre au-dessus de la grille
   boutique) : idem.

2) Live Chat qui ne s'affichait pas : diagnostic en cours (nécessite
   une inspection live du site réel, pas encore faite au moment de ce
   commit — voir la conversation/README pour la suite).
"""
import logging

from odoo import api, SUPERUSER_ID

_logger = logging.getLogger(__name__)


def migrate(cr, version):
    from odoo.addons.capsule_house_theme import run_theme_maintenance

    env = api.Environment(cr, SUPERUSER_ID, {})
    _logger.info(
        "capsule_house_theme: post-migrate 19.0.1.0.37 — traduction EN "
        "complétée (menu, meilleures ventes, bandeau d'annonce, hero "
        "boutique), oubliée en v.36."
    )
    run_theme_maintenance(env)
