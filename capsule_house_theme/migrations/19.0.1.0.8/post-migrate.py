# -*- coding: utf-8 -*-
"""
Rejoue run_theme_maintenance() après une mise à jour du module vers la
version 19.0.1.0.8.

Correctifs purement XML/CSS, tous liés à la comparaison maquette vs site
réel :

1. hero.xml : ajout du raccourci "+ Ajouter au panier" repris de la
   maquette, rattaché au 2e produit vedette réel (route native
   /shop/cart/update, formulaire classique sans JS custom) — affiché
   seulement s'il y a au moins 2 produits publiés, même logique que les
   cartes flottantes existantes.
2. homepage.css : ombre/glow au sol sous l'illustration du pod (pseudo-
   élément ::after), pour un rendu moins plat que la version précédente.

Rappel important (pas un bug, comportement volontaire) : les stats "0
modèles disponibles", l'absence du badge de note "4.9 · 2 340 avis" et
l'absence des badges "Nouveau"/"Promo" sur l'illustration sont dus à
l'absence de produits publiés et de vrais chiffres de note configurés —
ce module n'invente jamais ces données (voir README, section palette /
points à vérifier avec le client). Rien à corriger côté code pour ça :
ça se résout automatiquement dès que de vrais produits et, si souhaité,
un vrai rating_value/rating_count sont renseignés.
"""
import logging

from odoo import api, SUPERUSER_ID

_logger = logging.getLogger(__name__)


def migrate(cr, version):
    from odoo.addons.capsule_house_theme import run_theme_maintenance

    env = api.Environment(cr, SUPERUSER_ID, {})
    _logger.info(
        "capsule_house_theme: post-migrate 19.0.1.0.8 — rejeu de "
        "run_theme_maintenance() (raccourci panier hero + ombre au sol "
        "de l'illustration)."
    )
    run_theme_maintenance(env)
