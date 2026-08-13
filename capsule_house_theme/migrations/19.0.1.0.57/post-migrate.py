# -*- coding: utf-8 -*-
"""
Rejoue run_theme_maintenance() après une mise à jour du module vers la
version 19.0.1.0.57.

ANALYSE COMPLÈTE DES DEUX THÈMES (capsule_house_theme vs exocoms_theme),
demandée explicitement par le client après 8 échecs successifs (v49 à
v56) à faire apparaître le panneau Style du Website Builder sur le hero
de l'accueil, alors que le hero de /avis fonctionnait correctement avec
un balisage équivalent.

CAUSE RÉELLE TROUVÉE : ce n'était pas le balisage du hero (déjà
identique entre les deux pages depuis la v19.0.1.0.56), mais la façon
dont l'ACCUEIL LUI-MÊME était servi. Jusqu'ici :
  - '/' faisait un redirect natif Odoo vers `website.homepage_url`
    (= '/capsule-house/home'), posé par `_setup_homepage()`. C'est un
    vrai aller-retour HTTP côté navigateur, confirmé par capture
    DevTools client (`_setup_menus()` le documentait déjà pour un bug
    de surlignage de menu, sans qu'on ait fait le lien avec l'éditeur).
  - '/avis' en revanche est rendue en un seul rendu direct, sans
    redirect.
Comparaison avec exocoms_theme (qui sert '/' directement, sans jamais
passer par homepage_url) : c'est la SEULE différence structurelle
restante entre les deux sites une fois le balisage des heros aligné.

CORRECTIF : `CapsuleHouseWebsite` hérite maintenant de `index()` du
contrôleur natif `Website` via `@http.route()` SANS argument (donc
réutilise la route '/' existante, n'en crée PAS de nouvelle), avec la
même garde stricte que exocoms_theme (`_is_our_website` +
`super().index(**kw)` pour les 16 autres sites de la base mutualisée)
— pattern déjà éprouvé et jamais fautif en production chez exocoms.
La route dédiée '/capsule-house/home' est conservée en simple redirect
301 permanent vers '/' (favoris/liens déjà partagés), et
`website.homepage_url` est vidée par `_setup_homepage()`. Les menus
(Accueil) et les breadcrumbs des pages Aide/Entreprise pointent de
nouveau vers '/'.

Sécurité multi-site : AUCUNE nouvelle route enregistrée sur '/' (on
hérite et surcharge, comme exocoms_theme), fallback `super()`
systématique pour tout site qui n'est pas le nôtre — même précaution
que celle qui avait fait capoter une première tentative il y a
longtemps sur exocoms_theme, ici évitée dès le départ.
"""
import logging

from odoo import api, SUPERUSER_ID

_logger = logging.getLogger(__name__)


def migrate(cr, version):
    from odoo.addons.capsule_house_theme import run_theme_maintenance

    env = api.Environment(cr, SUPERUSER_ID, {})
    _logger.info(
        "capsule_house_theme: post-migrate 19.0.1.0.57 — l'accueil est "
        "servi directement sur '/' (surcharge héritée de Website.index(), "
        "pattern exocoms_theme), fin du redirect via homepage_url. Cause "
        "identifiée par analyse comparative complète des deux thèmes."
    )
    run_theme_maintenance(env)
