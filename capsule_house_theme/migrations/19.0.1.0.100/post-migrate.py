# -*- coding: utf-8 -*-
"""
Rejoue run_theme_maintenance() après une mise à jour du module vers la
version 19.0.1.0.100.

DEMANDE CLIENT (captures d'écran de exocoms_theme à l'appui) : "je veux
ces deux block a la fin de ma pages aceuil et pour le avis crée le meme
nombre qu on avais fait sur exocoms" — un bloc "Ce que nos clients
disent de nous" (3 témoignages) et un bloc "Paiements acceptés" (logos
de moyens de paiement), tous deux copiés depuis exocoms_theme, en fin
de page d'accueil.

CONFLIT IDENTIFIÉ avant implémentation : le bloc d'exocoms_theme
affiche 3 avis fabriqués (noms/citations inventés, hors-sujet — cette
maquette parle de terminaux de paiement/télécom, pas de maisons
modulaires) et 7 logos de paiement codés en dur, alors que ce module a
un principe explicite déjà en production ailleurs (models/avis.py,
controllers/main.py : "jamais de donnée fabriquée"). Vérifié en direct
avant toute décision :
- /avis (avis publiés) : "No reviews yet" — 0 avis réel aujourd'hui.
- /odoo/payment-providers : Virement + Paiement à la livraison =
  Désactivé, tous les autres = non installés — aucun moyen de paiement
  réellement actif aujourd'hui.

Le client a été explicitement consulté (question à choix) et a
confirmé : bloc avis branché sur les VRAIS avis (recommandé), bloc
paiement affiché seulement une fois un vrai fournisseur configuré côté
client.

Implémentation :
- views/partials/home_testimonials.xml (+ /capsule-house/
  testimonials-data.json dans controllers/main.py) : jusqu'à 3 VRAIS
  avis publiés (capsule.house.avis, state='published'), avatar =
  initiale du vrai nom (même convention que .ch-avis-avatar sur
  /avis). Section masquée (d-none) tant qu'aucun avis n'est publié.
- views/partials/home_payment_methods.xml (+ /capsule-house/
  payment-methods-data.json) : SEULS les payment.provider réellement
  à l'état 'enabled', affichés en badges texte (pas de logo de marque
  non vérifié). Section masquée tant qu'aucun n'est configuré.
- Les deux sont peuplées côté client par static/src/js/main.js
  (initTestimonialsSection / initPaymentMethodsSection), même principe
  que hero.xml/initHeroDynamicContent (arch 100% statique, condition
  nécessaire pour qu'Odoo marque la section comme un bloc éditable) —
  aucune donnée fabriquée, dégradation gracieuse (section masquée) si
  le fetch échoue.
- t-called depuis home.xml, en tout dernier (juste avant le
  placeholder oe_structure_ch_home_bottom), conformément à la demande
  "à la fin de ma page accueil".

Les deux blocs sont donc livrés dès aujourd'hui mais INVISIBLES sur le
site en production tant qu'aucune vraie donnée n'existe : ils
apparaîtront automatiquement dès qu'un avis sera publié et/ou qu'un
moyen de paiement sera activé, sans nouvelle mise à jour de code.
"""
import logging

from odoo import api, SUPERUSER_ID

_logger = logging.getLogger(__name__)


def migrate(cr, version):
    from odoo.addons.capsule_house_theme import run_theme_maintenance

    env = api.Environment(cr, SUPERUSER_ID, {})
    _logger.info(
        "capsule_house_theme: post-migrate 19.0.1.0.100 — blocs avis "
        "clients (jusqu'à 3 vrais avis publiés) et moyens de paiement "
        "(fournisseurs réellement 'enabled' uniquement) ajoutés en fin "
        "d'accueil, masqués tant qu'aucune vraie donnée n'existe "
        "(aucun contenu fabriqué, contrairement au modèle exocoms_theme "
        "copié initialement par le client)."
    )
    run_theme_maintenance(env)
