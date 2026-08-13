# -*- coding: utf-8 -*-
"""
Rejoue run_theme_maintenance() après une mise à jour du module vers la
version 19.0.1.0.83.

Corrige le VRAI bug derrière l'espacement des titres de section sur
/nos-gammes/<slug>, que les tentatives 19.0.1.0.81 et .82 n'avaient pas
résolu — le client l'a confirmé par capture d'écran après déploiement :
"Technical specifications" et "Options" quasiment collés au contenu
précédent, malgré le correctif.

Cause racine identifiée en relisant nos_gammes.xml : chaque titre
(Formats, Spécifications techniques, Équipements inclus, Options) est
seul enfant `<h2>` de son propre `<div>` wrapper. Le sélecteur CSS
`:first-of-type` utilisé dans les versions .81/.82 regarde le premier
enfant DE SON PARENT DIRECT — comme chaque h2 est SEUL dans son div,
il est "premier de son type" dans TOUS les cas, pas seulement pour le
tout premier titre de la page. Résultat : la règle qui devait annuler
l'espacement UNIQUEMENT sur le premier titre ("Formats") l'annulait en
réalité sur tous, et celle qui ajoutait l'espacement ne s'appliquait
donc jamais qu'à "Formats" (déjà correct par coïncidence visuelle).

Fix : chaque `<div>` wrapper de section porte maintenant la classe
`.ch-gamme-section` (nos_gammes.xml). Le CSS utilise un sélecteur de
fratrie général (`.ch-gamme-section ~ .ch-gamme-section
.ch-gamme-section-title`) qui cible correctement "un titre dans une
section précédée par au moins une autre section" — robuste quelle que
soit la structure DOM interne de chaque section, contrairement à
`:first-of-type`.

Fichiers modifiés : views/pages/nos_gammes.xml (classe ajoutée sur 4
wrappers), static/src/css/pages.css (règle réécrite).
"""
import logging

from odoo import api, SUPERUSER_ID

_logger = logging.getLogger(__name__)


def migrate(cr, version):
    from odoo.addons.capsule_house_theme import run_theme_maintenance

    env = api.Environment(cr, SUPERUSER_ID, {})
    _logger.info(
        "capsule_house_theme: post-migrate 19.0.1.0.83 — bug réel de "
        "l'espacement des titres de section corrigé (le sélecteur CSS "
        ":first-of-type des versions .81/.82 ne fonctionnait pas comme "
        "prévu à cause de la structure DOM ; remplacé par un sélecteur de "
        "fratrie fiable via la classe .ch-gamme-section)."
    )
    run_theme_maintenance(env)
