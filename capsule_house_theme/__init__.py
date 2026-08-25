# -*- coding: utf-8 -*-
"""
Post-init Hook & Routines de Maintenance du Thème Odoo
=====================================================
Module      : capsule_house_theme (Thème & Configuration du site Odoo)
Fichier     : __init__.py / hooks.py
Auteur      : Équipe Dev Odoo
Dernière modif: 2026-08-25
Contexte    : Point d'entrée principal pour l'exécution du post_init_hook Odoo et des
             fonctions d'alignement orchestrées via `setup_utils.py`.

Règles Métier & Séquencement d'Initialisation :
- Isolation & Sécurité : Initialise la société et accorde les accès administrateurs avant toute opération.
- Provisionning Web : Prépare l'instance du site, sa liste de prix et les configurations i18n (FR/EN).
- Assets & UI : Restaure le logo, invalide les caches d'assets, applique les surcharges QWeb et la feuille de style.
- E-Commerce : Structuration des catégories, configuration de la grille /shop, menus, filtres et publication produits.
"""

import logging

from . import controllers
from . import models
from .setup_utils import (
    _get_company,
    _grant_company_access,
    _get_website,
    _setup_pricelist,
    _setup_languages,
    _reload_native_translations,
    _set_logo,
    _setup_homepage,
    _setup_domain,
    _setup_website_priority,
    _setup_theme_assets,
    _invalidate_frontend_assets,
    _scope_layout_views,
    _reset_customized_views,
    _setup_livechat,
    _clean_demo_data,
    _setup_shop_categories,
    _setup_shop_display,
    _setup_shop_grid_design,
    _setup_menus,
    _setup_shop_filters,
    _publish_our_products,
    _attach_shop_filters_to_products,
)

_logger = logging.getLogger(__name__)


# -----------------------------------------------------------------------------
# ORCHESTRATEUR PRINCIPAL DE MAINTENANCE & INITIALISATION
# -----------------------------------------------------------------------------

def run_theme_maintenance(env):
    """
    SOURCE : Séquence d'Initialisation du Thème Odoo
    Exécute dans un ordre strict toutes les routines de configuration du site,
    du paramétrage de la société initiale jusqu'à la publication des produits sur la boutique.
    
    :param env: Odoo Environment (api.Environment)
    :return: Recordset du site web configuré (website)
    """
    # 1. Isolation multi-company et résolutions d'accès backend/frontend (403 Fixes)
    company = _get_company(env)
    _grant_company_access(env, company)
    
    # 2. Provisionning de l'instance Web et tarification
    website = _get_website(env, company)
    _setup_pricelist(env, website, company)
    
    # 3. Internationalisation et rechargement des traductions natifs (FR par défaut, EN)
    _setup_languages(env, website)
    _reload_native_translations(env)
    
    # 4. Brand assets, domaine, routage de la page d'accueil et priorité de contrôleur
    _set_logo(env, website)
    _setup_homepage(env, website)
    _setup_domain(env, website)
    _setup_website_priority(env, website)
    
    # 5. Compilation SCSS/JS, invalidation des caches ir.attachment et scoping des vues
    _setup_theme_assets(env, website)
    _invalidate_frontend_assets(env, website)
    _scope_layout_views(env, website)
    _reset_customized_views(env)
    
    # 6. Activation du canal de communication et ménage des données de démo
    _setup_livechat(env, website)
    _clean_demo_data(env, website)
    
    # 7. Taxonomie boutique, affichage des grilles produits et génération du menu Header
    categories = _setup_shop_categories(env, website)
    _setup_shop_display(env, website)
    _setup_shop_grid_design(env, website)
    _setup_menus(env, website, categories)
    
    # 8. Filtres e-commerce (product.attribute) et publication automatique du catalogue
    _setup_shop_filters(env)
    _publish_our_products(env, website, company)
    _attach_shop_filters_to_products(env, website)
    
    _logger.info(
        "capsule_house_theme: run_theme_maintenance terminé (website_id=%s, "
        "company_id=%s).", website.id, company.id,
    )
    return website


# -----------------------------------------------------------------------------
# ODOO HOOK DE POST-INSTALLATION
# -----------------------------------------------------------------------------

def post_init_hook(env):
    """
    SOURCE : Manifest Odoo (`post_init_hook`)
    Point de réaction automatique déclenché par Odoo immédiatement après
    l'installation du module `capsule_house_theme`.
    """
    run_theme_maintenance(env)