# -*- coding: utf-8 -*-
"""
Rejoue run_theme_maintenance() après une mise à jour du module vers la
version 19.0.1.0.66.

Demande client : "regarde exocoms et ajoute ce qui est nécessaire pour
capsule house et si tu peux l'améliorer tu le fais". Comparaison
complète des deux modules (structure de fichiers, controllers, vues) —
la plupart des éléments d'exocoms_theme sans équivalent ici sont soit
volontairement différents (ex. /contactus natif au lieu d'une page
contact custom, décision déjà actée), soit demandent du contenu réel
non disponible (page Services/domaines d'expertise avec 3 sous-pages
métier type informatique/télécom/monétique — propres à l'activité
d'Exocoms, pas transposables sans fabriquer du contenu ; page Emplois
avec de vraies offres ; page Cas clients avec de vraies photos de
chantiers).

Deux éléments étaient en revanche réellement portables sans rien
inventer, ajoutés ici sur la home (views/partials/home_trust.xml) :

1. Témoignages (.ch-testimonials) : carousel alimenté par les VRAIS
   avis publiés (capsule.house.avis), même mécanisme qu'exocoms
   (_get_home_avis_context, nouveau dans controllers/main.py). Aucun
   avis fabriqué : état vide explicite si aucun avis publié.

2. Réassurance (.ch-why-us) : contrairement aux 4 promesses génériques
   d'exocoms (non vérifiées pour notre activité), les 4 items repris
   ici ne font que reformater des faits DÉJÀ publiés et validés
   ailleurs sur ce site : annulation 48h (aide_retours.xml), livraison
   6 semaines France métropolitaine (aide_livraison.xml), garantie
   constructeur 10 ans (aide_garantie.xml), paiement 3x sans frais dès
   1000€ (hero.xml, aide_faq.xml).

Amélioration apportée par rapport à l'original exocoms (demande
explicite : "si tu peux l'améliorer tu le fais") : le script de
défilement automatique du carousel témoignages, en <script> inline
dans le template QWeb chez exocoms, est déplacé dans main.js
(initTestimonialsCarousel) — cohérent avec le reste de ce module, où
tout le JS du thème vit dans main.js, jamais dans les vues.

La bande "moyens de paiement" (logos Visa/Mastercard/PayPal/Amex...)
d'exocoms n'est PAS reprise : elle affirmerait des moyens de paiement
dont ce module n'a aucune confirmation qu'ils sont réellement
configurés côté website_sale pour ce site.
"""
import logging

from odoo import api, SUPERUSER_ID

_logger = logging.getLogger(__name__)


def migrate(cr, version):
    from odoo.addons.capsule_house_theme import run_theme_maintenance

    env = api.Environment(cr, SUPERUSER_ID, {})
    _logger.info(
        "capsule_house_theme: post-migrate 19.0.1.0.66 — ajout témoignages "
        "+ réassurance sur la home (views/partials/home_trust.xml), repris "
        "d'exocoms_theme et adaptés avec uniquement des faits déjà publiés "
        "sur ce site."
    )
    run_theme_maintenance(env)
