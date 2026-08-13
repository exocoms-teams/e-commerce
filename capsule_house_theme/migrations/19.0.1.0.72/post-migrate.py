# -*- coding: utf-8 -*-
"""
Rejoue run_theme_maintenance() après une mise à jour du module vers la
version 19.0.1.0.72.

Suite directe de la 19.0.1.0.71 (page /nos-gammes + section usages sur
l'accueil). Le client a demandé deux changements supplémentaires le
même jour (2026-08-13) :

1. "même nos gamme doit apparaître sur accueil" — le filmstrip des 5
   gammes (Capsule/Cabine/Dôme/Modulaire/Pliable), jusque-là visible
   uniquement sur /nos-gammes, est repris tel quel dans une nouvelle
   section de l'accueil (voir views/partials/home_gammes.xml), juste
   avant la section usages. La page /nos-gammes (index + détail par
   gamme) continue d'exister : la section accueil est un aperçu qui
   pointe vers elle, pas un remplacement.

2. "enlève nos modèle et nos gamme sur le header" — les entrées de menu
   "Nos gammes" et "Nos modèles" sont retirées du header (_setup_menus,
   __init__.py). Les deux pages et leurs routes (/nos-gammes,
   /nos-modeles) restent pleinement fonctionnelles et accessibles
   (depuis l'accueil et les liens croisés), simplement plus référencées
   dans la nav principale — cohérent avec le fait que leur contenu
   (gammes) est désormais visible dès l'arrivée sur le site.

Nouveau fichier : views/partials/home_gammes.xml. Réutilise les classes
CSS existantes (.ch-gammes-filmstrip, .ch-gamme-card, voir pages.css,
v19.0.1.0.71) sans en ajouter de nouvelles.
"""
import logging

from odoo import api, SUPERUSER_ID

_logger = logging.getLogger(__name__)


def migrate(cr, version):
    from odoo.addons.capsule_house_theme import run_theme_maintenance

    env = api.Environment(cr, SUPERUSER_ID, {})
    _logger.info(
        "capsule_house_theme: post-migrate 19.0.1.0.72 — section gammes "
        "ajoutée sur l'accueil (filmstrip des 5 gammes, réutilise "
        "/nos-gammes) ; entrées de menu 'Nos gammes' et 'Nos modèles' "
        "retirées du header (pages/routes conservées, plus référencées "
        "dans la nav)."
    )
    run_theme_maintenance(env)
