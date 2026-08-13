# -*- coding: utf-8 -*-
"""
Rejoue run_theme_maintenance() après une mise à jour du module vers la
version 19.0.1.0.71.

Ajoute la page "Nos gammes" (/nos-gammes, index + détail par gamme) et
la section "usages" de l'accueil, en réponse à une série d'échanges
avec le client (2026-08-13) sur la refonte de la taxonomie produit :

1. Studio/Duo/Panorama, jusque-là des catégories boutique de premier
   niveau (entrées de menu directes + page /nos-modeles), deviennent
   des FORMATS au sein d'une gamme "Capsule" ("studio duo et panorama
   ne sont que les format et accessoire seront les options et
   équipement").
2. Le client a demandé 5 gammes au total : Capsule, Cabine, Dôme,
   Modulaire, Pliable. Seule Capsule a des données réelles/indicatives
   pour l'instant ; les 4 autres sont marquées "à confirmer" (listes
   vides intentionnelles, jamais de contenu inventé).
3. Sur les specs techniques : le client a explicitement autorisé la
   reprise de valeurs indicatives issues d'un standard du marché
   (capsule-home.fr) "on modifiera plus tard", tout en confirmant que
   les normes françaises réellement citées (NF EN 1279, NF EN 410,
   NF EN 14351-1, NF C 15-100) sont, elles, vérifiables.
4. Studio/Duo/Panorama sont retirés des entrées de menu du header
   ("supprime studio duo et panorama dans le header") : le header
   n'affiche plus que "Nos gammes" (+ "Accessoires" restée seule
   entrée directe de catégorie) au lieu des 4 catégories individuelles.
5. Le concept de page "Application" séparée (usages : Logement,
   Bureau, Résidence secondaire, Location & Airbnb, Accessoires) est
   abandonné au profit d'une section directement sur l'accueil ("il ne
   faut plus de page application mais le faire directement sur
   accueil"), avec un intitulé qui évite le mot "gamme" pour ne pas
   mélanger les deux concepts.

/nos-modeles est explicitement conservée telle quelle en parallèle
("on laisse nos modèles") : ce n'est pas un remplacement, ce sont deux
pages distinctes qui coexistent.

Nouveaux fichiers : views/pages/nos_gammes.xml,
views/partials/home_usages.xml. Nouvelles constantes __init__.py :
GAMMES_DATA, USAGES_DATA. Nouvelles routes controllers/main.py :
nos_gammes(), nos_gammes_detail(). CSS : pages.css (.ch-gamme-*),
homepage.css (.ch-usage-*).
"""
import logging

from odoo import api, SUPERUSER_ID

_logger = logging.getLogger(__name__)


def migrate(cr, version):
    from odoo.addons.capsule_house_theme import run_theme_maintenance

    env = api.Environment(cr, SUPERUSER_ID, {})
    _logger.info(
        "capsule_house_theme: post-migrate 19.0.1.0.71 — ajout de la page "
        "/nos-gammes (5 gammes : Capsule/Cabine/Dôme/Modulaire/Pliable) et "
        "de la section usages sur l'accueil ; Studio/Duo/Panorama retirés "
        "du menu (deviennent des formats de la gamme Capsule) ; "
        "/nos-modeles conservée inchangée."
    )
    run_theme_maintenance(env)
