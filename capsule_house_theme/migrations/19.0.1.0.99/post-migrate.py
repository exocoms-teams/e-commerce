# -*- coding: utf-8 -*-
"""
Rejoue run_theme_maintenance() après une mise à jour du module vers la
version 19.0.1.0.99.

DEMANDE CLIENT : "on a mis en sous-catégorie les formats de la gamme
correspondant [Capsule = Studio/Duo/Panorama], je voudrais pareil pour
les autres catégories." Jusqu'ici, seule la gamme Capsule avait ses
formats déclarés comme sous-catégories boutique (SHOP_SUBCATEGORIES,
constants.py) — Cabine/Dôme/Modulaire/Pliable n'en avaient aucune,
malgré les correctifs récents (19.0.1.0.98) qui affichent maintenant
"Détails disponibles" pour les 5 gammes sur l'accueil.

Fix : SHOP_SUBCATEGORIES étendu avec les formats de chaque gamme, tels
que définis dans GAMMES_DATA (data_definition/__init__.py, clé
'formats') :
- Cabine : Solo / Bureau, Comfort, Lodge
- Dôme : Compact, Confort, Panoramique
- Modulaire : Module simple, Module double, Module triple
- Pliable : Compact, Confort, Panoramique

ATTENTION collision de noms évitée : _setup_shop_categories()
(setup_utils.py) recherche/rattache chaque sous-catégorie par son NOM
SEUL (pas par couple nom+parent) — deux sous-catégories de gammes
différentes portant le même nom se « voleraient » l'une l'autre au fil
des synchronisations (mauvais parent_id). Or GAMMES_DATA donne EXACTEMENT
les mêmes noms de formats pour Dôme et Pliable ('Compact', 'Confort',
'Panoramique'). Ces deux gammes ont donc été préfixées par leur nom
('Dôme Compact', 'Pliable Compact', etc.) pour rester uniques ; Cabine et
Modulaire avaient déjà des noms uniques, repris tels quels.

Fichier modifié : constants.py (SHOP_SUBCATEGORIES).
_setup_shop_categories() (déjà existante, inchangée) crée/rattache
automatiquement ces nouvelles sous-catégories au prochain passage de
run_theme_maintenance — les produits déjà en boutique ne sont pas
réaffectés automatiquement (à faire manuellement côté client si besoin).
"""
import logging

from odoo import api, SUPERUSER_ID

_logger = logging.getLogger(__name__)


def migrate(cr, version):
    from odoo.addons.capsule_house_theme import run_theme_maintenance

    env = api.Environment(cr, SUPERUSER_ID, {})
    _logger.info(
        "capsule_house_theme: post-migrate 19.0.1.0.99 — sous-catégories "
        "boutique créées pour les formats de Cabine/Dôme/Modulaire/"
        "Pliable (même principe que Capsule=Studio/Duo/Panorama), "
        "Dôme/Pliable préfixées pour éviter la collision de noms "
        "(formats identiques dans GAMMES_DATA)."
    )
    run_theme_maintenance(env)
