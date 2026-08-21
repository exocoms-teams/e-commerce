# -*- coding: utf-8 -*-
"""
Rejoue run_theme_maintenance() après une mise à jour du module vers la
version 19.0.1.0.88.

Retour client : "tu n'as pas fait la même chose sur avis et home, le
style ne s'affiche pas, je t'avais demandé de faire comme ça pour
toutes les pages de mon site". Deux angles morts corrigés :

1) Accueil (home_gammes.xml, home_usages.xml) : en 19.0.1.0.87, seules
   les 5 cartes de chaque section avaient été mises dans une zone
   oe_structure. Le titre de section (badge + h2 "Nos gammes" / "À quoi
   servira votre pod ?") restait, lui, en dehors de toute zone
   éditable — donc non cliquable dans le Website Builder, ce qui a pu
   donner l'impression que "l'accueil ne marche pas" en cliquant
   dessus. Corrigé : ce titre est maintenant lui aussi dans un
   <div class="oe_structure"> avec un <section> par langue.

2) Avis (avis_content.xml) : cette page avait été volontairement
   exclue de la conversion en 19.0.1.0.84, car son contenu est
   majoritairement DYNAMIQUE (stats calculées en base, grille d'avis
   réels, formulaire de dépôt avec CSRF + JS de notation). Le client a
   confirmé vouloir "toutes les pages du site" — le seul contenu
   RÉELLEMENT statique de cette page (le titre + le texte d'intro du
   formulaire, "Partagez votre expérience" / "Share your experience")
   est maintenant converti en bloc éditable, comme le reste du site.

   Restent volontairement NON convertis sur /avis, pour des raisons
   fonctionnelles (pas une simple préférence de style) :
   - le bloc stats (moyenne, barres de répartition) : donnée calculée,
     pas du texte ;
   - les boutons de filtre par note : dépendent de data-filter + JS ;
   - la grille d'avis : boucle sur les avis RÉELS en base ;
   - les champs du formulaire lui-même (star picker, inputs, CSRF) :
     les exposer au glisser-déposer risquerait de casser l'envoi
     d'avis. Si le client souhaite malgré tout les rendre éditables, il
     faudra le redemander explicitement en connaissance de ce risque.

   shop.xml (bandeau au-dessus de la grille boutique) reste également
   non converti : ce n'est pas une page à nous, c'est un patch xpath
   sur la vue native website_sale.products partagée par toute
   l'instance mutualisée — même famille de risque, à traiter séparément
   si demandé.

Fichiers modifiés : views/partials/home_gammes.xml,
views/partials/home_usages.xml, views/partials/avis_content.xml.
"""
import logging

from odoo import api, SUPERUSER_ID

_logger = logging.getLogger(__name__)


def migrate(cr, version):
    from odoo.addons.capsule_house_theme import run_theme_maintenance

    env = api.Environment(cr, SUPERUSER_ID, {})
    _logger.info(
        "capsule_house_theme: post-migrate 19.0.1.0.88 — titres de "
        "section de l'accueil (Gammes/Usages) et intro du formulaire "
        "Avis convertis en blocs éditables ; le reste de /avis "
        "(stats, filtres, grille d'avis réels, formulaire) reste "
        "protégé car fonctionnel/dynamique."
    )
    run_theme_maintenance(env)
