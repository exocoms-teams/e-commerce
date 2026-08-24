# -*- coding: utf-8 -*-
import logging

_logger = logging.getLogger(__name__)

CONFIG_WEBSITE_ID_KEY = 'capsule_house_theme.website_id'
CONFIG_ASSETS_FIX_KEY = 'capsule_house_theme.frontend_assets_regenerated_v1'
CONFIG_LOGO_APPLIED_KEY = 'capsule_house_theme.logo_applied_v1'
CONFIG_DOMAIN_LIVE_KEY = 'capsule_house_theme.domain_live'

COMPANY_NAME = 'Exocoms Group'
WEBSITE_NAME = 'Capsule House'
WEBSITE_DOMAIN = 'capsule-house.fr'
HOMEPAGE_ROUTE = '/capsule-house/home'

LOGO_PATH = ('static', 'src', 'img', 'capsule-house-logo.png')

THEME_ASSETS = {
    'variables.css': 'capsule_house_theme/static/src/css/variables.css',
    'base.css': 'capsule_house_theme/static/src/css/base.css',
    'layout.css': 'capsule_house_theme/static/src/css/layout.css',
    'homepage.css': 'capsule_house_theme/static/src/css/homepage.css',
    'shop.css': 'capsule_house_theme/static/src/css/shop.css',
    'odoo-integration.css': 'capsule_house_theme/static/src/css/odoo-integration.css',
    'pages.css': 'capsule_house_theme/static/src/css/pages.css',
    'legal.css': 'capsule_house_theme/static/src/css/legal.css',
    'main.js': 'capsule_house_theme/static/src/js/main.js',
}

SCOPED_VIEW_XML_IDS = [
    'capsule_house_theme.theme_announce_bar',
    'capsule_house_theme.theme_footer',
    'capsule_house_theme.theme_layout',
    'capsule_house_theme.partial_hero',
    'capsule_house_theme.partial_hero_fr',
    'capsule_house_theme.partial_hero_en',
    'capsule_house_theme.partial_featured_products',
    'capsule_house_theme.page_home',
    'capsule_house_theme.page_shop',
    'capsule_house_theme.avis_page',
    'capsule_house_theme.avis_hero',
    'capsule_house_theme.avis_content',
    'capsule_house_theme.avis_hero_fr',
    'capsule_house_theme.avis_hero_en',
    'capsule_house_theme.aide_sidebar',
    'capsule_house_theme.aide_livraison_page',
    'capsule_house_theme.aide_retours_page',
    'capsule_house_theme.aide_garantie_page',
    'capsule_house_theme.aide_faq_page',
    'capsule_house_theme.entreprise_nav',
    'capsule_house_theme.entreprise_apropos_page',
    'capsule_house_theme.entreprise_concept_page',
    'capsule_house_theme.mentions_legales_page',
    'capsule_house_theme.cgv_page',
    'capsule_house_theme.confidentialite_page',
    'capsule_house_theme.page_nos_gammes_detail',
    'capsule_house_theme.partial_home_usages',
    'capsule_house_theme.partial_home_gammes',
]

RESETTABLE_VIEW_XML_IDS = [
    'capsule_house_theme.partial_home_gammes',
    'capsule_house_theme.partial_home_usages',
]

SHOP_CATEGORIES = ['Capsule', 'Cabine', 'Dôme', 'Modulaire', 'Pliable', 'Accessoires']

SHOP_SUBCATEGORIES = {
    'Capsule': ['Studio', 'Duo', 'Panorama'],
}

SHOP_FILTER_ATTRIBUTES = {
    'Surface (m²)': ['15-20 m²', '20-30 m²', '30-45 m²'],
}

SHOP_DESIGN_CLASSES = (
    'o_wsale_products_opt_name_color_regular '
    'o_wsale_products_opt_thumb_cover '
    'o_wsale_products_opt_img_secondary_show '
    'o_wsale_products_opt_img_hover_zoom_out_light '
    'o_wsale_products_opt_has_cta '
    'o_wsale_products_opt_has_wishlist '
    'o_wsale_products_opt_has_comparison '
    'o_wsale_products_opt_actions_inline '
    'o_wsale_products_opt_wishlist_inline '
    'o_wsale_products_opt_actions_promote '
    'o_wsale_products_opt_cc '
    'o_wsale_products_opt_cc1 '
    'o_wsale_products_opt_rounded_4 '
    'o_wsale_products_opt_thumb_6_5 '
    'o_wsale_products_opt_layout_catalog '
    'o_wsale_products_opt_design_chips'
)