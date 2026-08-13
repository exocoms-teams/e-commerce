# -*- coding: utf-8 -*-
"""
Rejoue run_theme_maintenance() après une mise à jour du module vers la
version 19.0.1.0.75.

Remplace Studio/Duo/Panorama par les 5 gammes comme onglets de premier
niveau de la page /shop native de website_sale — demande client
explicite, capture d'écran des onglets réels à l'appui : "accessoire
reste sauf studio duo et panorama doivent partir et mettre à la place
nos différentes gammes".

Mécanisme (voir _setup_shop_categories, __init__.py) :
- SHOP_CATEGORIES passe de ['Studio', 'Duo', 'Panorama', 'Accessoires']
  à ['Capsule', 'Cabine', 'Dôme', 'Modulaire', 'Pliable', 'Accessoires']
  — ce sont désormais ces 6 catégories qui sont créées/synchronisées
  comme catégories de PREMIER NIVEAU (parent_id vide), donc les seules
  affichées en onglets par la page /shop native.
- SHOP_SUBCATEGORIES = {'Capsule': ['Studio', 'Duo', 'Panorama']} :
  Studio/Duo/Panorama ne sont PAS supprimées ni réaffectées — elles
  sont simplement REPARENTÉES sous "Capsule" (parent_id posé). Comme
  website_sale n'affiche en onglets que les catégories sans parent,
  ce simple reparentage suffit à les faire disparaître des onglets,
  SANS toucher aux produits déjà rattachés à ces catégories (aucune
  réaffectation nécessaire, aucune donnée perdue).
- La page /nos-modeles (Studio/Duo/Panorama/Accessoires) est
  volontairement DÉCOUPLÉE de SHOP_CATEGORIES via la nouvelle
  constante NOS_MODELES_CATEGORIES (figée), pour ne pas changer son
  contenu suite à cette évolution — demande client répétée : "on
  laisse nos modèles". Voir controllers/main.py, nos_modeles().

Idempotent, comme tout le reste de run_theme_maintenance : rejouable
sans dupliquer ni casser l'existant.
"""
import logging

from odoo import api, SUPERUSER_ID

_logger = logging.getLogger(__name__)


def migrate(cr, version):
    from odoo.addons.capsule_house_theme import run_theme_maintenance

    env = api.Environment(cr, SUPERUSER_ID, {})
    _logger.info(
        "capsule_house_theme: post-migrate 19.0.1.0.75 — Studio/Duo/"
        "Panorama reparentées sous 'Capsule' (retirées des onglets de "
        "premier niveau de /shop, produits déjà rattachés inchangés) ; "
        "les 5 gammes (Capsule/Cabine/Dôme/Modulaire/Pliable) + "
        "Accessoires deviennent les catégories de premier niveau ; "
        "/nos-modeles découplée via NOS_MODELES_CATEGORIES (inchangée)."
    )
    run_theme_maintenance(env)
