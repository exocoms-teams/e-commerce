# -*- coding: utf-8 -*-
import logging

_logger = logging.getLogger(__name__)

CONFIG_WEBSITE_ID_KEY = 'capsule_house_theme.website_id'

# Garde-fou pour _invalidate_frontend_assets() : ce nettoyage ne doit
# tourner qu'UNE SEULE FOIS (pas à chaque passage du cron horaire), voir le
# docstring de cette fonction pour le contexte du bug qu'elle corrige.

CONFIG_ASSETS_FIX_KEY = 'capsule_house_theme.frontend_assets_regenerated_v1'
CONFIG_LOGO_APPLIED_KEY = 'capsule_house_theme.logo_applied_v1'


# Garde-fou pour _set_logo() : appliquer notre logo UNE SEULE FOIS,
# jamais à chaque passage (cron horaire / migration), voir le docstring
# de cette fonction pour le contexte du bug qu'il corrige (website.logo
# déjà non-vide par défaut sur un nouveau site Odoo, donc jamais écrasé
# par l'ancienne condition `if website.logo: return`).
COMPANY_NAME = 'Exocoms Group'
WEBSITE_NAME = 'Capsule House'
LOGO_PATH = ('static', 'src', 'img', 'capsule-house-logo.png')


# Ancienne route dédiée de l'accueil (jusqu'à la 19.0.1.0.56). Depuis la
# 19.0.1.0.57, l'accueil est servi directement sur '/' (voir
# CapsuleHouseWebsite.index() dans controllers/main.py) ; cette constante
# ne sert plus qu'à documenter/retrouver l'ancienne URL, conservée en
# redirect permanent (homepage_legacy_redirect) pour les favoris/liens
# déjà partagés.
HOMEPAGE_ROUTE = '/capsule-house/home'

# Domaine de prod cible. Volontairement PAS posé automatiquement sur le
# site tant que ir.config_parameter 'capsule_house_theme.domain_live'
# n'est pas explicitement mis à '1' : voir _setup_domain(). Un domaine posé
# avant que le DNS ne pointe vraiment dessus casse le sélecteur de site /
# la preview sur l'environnement de dev-staging (DNS_PROBE_FINISHED_NXDOMAIN).

CONFIG_DOMAIN_LIVE_KEY = 'capsule_house_theme.domain_live'
WEBSITE_DOMAIN = 'capsule-house.fr'

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


# Vues (external ids) livrées par ce module qui doivent être scopées à notre
# seul site après installation, sans quoi un ir.ui.view avec website_id=False
# s'appliquerait par défaut à TOUS les sites de la base partagée.


SCOPED_VIEW_XML_IDS = [
    'capsule_house_theme.theme_announce_bar',
    'capsule_house_theme.theme_footer',
    'capsule_house_theme.theme_layout',
    'capsule_house_theme.partial_hero',
    # Ajoutés en 19.0.1.0.51 (hero scindé en FR/EN, voir hero.xml).
    'capsule_house_theme.partial_hero_fr',
    'capsule_house_theme.partial_hero_en',
    'capsule_house_theme.partial_featured_products',
    'capsule_house_theme.page_home',
    'capsule_house_theme.page_shop',
    # Ajoutés en 19.0.1.0.35 (page /avis, voir models/avis.py).
    'capsule_house_theme.avis_page',
    'capsule_house_theme.avis_hero',
    'capsule_house_theme.avis_content',
    # Ajoutés en 19.0.1.0.36 (avis_hero scindé en FR/EN, voir
    # avis_hero.xml et README "Traduction des pages").
    'capsule_house_theme.avis_hero_fr',
    'capsule_house_theme.avis_hero_en',
    # Ajoutés en 19.0.1.0.46 (pages Aide : Livraison/Retours/Garantie/
    # FAQ, colonne "Aide" du footer — voir README).
    'capsule_house_theme.aide_sidebar',
    'capsule_house_theme.aide_livraison_page',
    'capsule_house_theme.aide_retours_page',
    'capsule_house_theme.aide_garantie_page',
    'capsule_house_theme.aide_faq_page',
    # Ajoutés en 19.0.1.0.47 (pages Entreprise : À propos/Le concept,
    # colonne "Entreprise" du footer — "Contact" reste natif /contactus,
    # jamais construit par ce module — voir README).
    'capsule_house_theme.entreprise_nav',
    'capsule_house_theme.entreprise_apropos_page',
    'capsule_house_theme.entreprise_concept_page',
    # Ajoutés en 19.0.1.0.64 (pages légales : Mentions légales/CGV/
    # Confidentialité — liens du footer cassés depuis le début du projet,
    # détecté par l'outil SEO natif d'Odoo — voir README).
    'capsule_house_theme.mentions_legales_page',
    'capsule_house_theme.cgv_page',
    'capsule_house_theme.confidentialite_page',
    # NB : page_nos_modeles (page /nos-modeles, livrée en 19.0.1.0.67 sur
    # le modèle de "Nos services" d'exocoms_theme) a été RETIRÉE en
    # 19.0.1.0.76 — demande client explicite : "la page nos modèles doit
    # disparaître sur mon code". Voir controllers/main.py (nos_modeles()
    # redirige désormais vers '/').
    # Ajoutés en 19.0.1.0.71 (pages /nos-gammes/<slug> : détail par
    # gamme, voir nos_gammes.xml et GAMMES_DATA ci-dessus), et section
    # "usages" de l'accueil (remplace l'idée d'une page Application
    # séparée, voir home_usages.xml et USAGES_DATA).
    # NB : page_nos_gammes (l'ancien index /nos-gammes) a été RETIRÉE en
    # 19.0.1.0.73 — demande client explicite, voir nos_gammes.xml et
    # controllers/main.py (nos_gammes() redirige désormais vers '/').
    'capsule_house_theme.page_nos_gammes_detail',
    'capsule_house_theme.partial_home_usages',
    # Ajouté en 19.0.1.0.72 (section gammes de l'accueil, voir
    # home_gammes.xml).
    'capsule_house_theme.partial_home_gammes',
]

# Catégories boutique (product.public.category), niveau top (celles qui
# apparaissent comme onglets sur la page /shop native de website_sale).
#
# CHANGEMENT (v19.0.1.0.75) : jusqu'ici Studio/Duo/Panorama/Accessoires
# étaient les 4 catégories de premier niveau. Demande client, capture
# d'écran des onglets /shop à l'appui : "accessoire reste sauf studio
# duo et panorama doivent partir et mettre à la place nos différentes
# gammes" — Studio/Duo/Panorama ne doivent plus apparaître comme des
# onglets à eux seuls, remplacés par les 5 gammes (cohérent avec
# GAMMES_DATA : Studio/Duo/Panorama sont des FORMATS de la gamme
# Capsule, pas des catégories indépendantes).
#
# Studio/Duo/Panorama ne sont PAS supprimés : voir SHOP_SUBCATEGORIES
# ci-dessous, ils deviennent des sous-catégories de "Capsule"
# (parent_id posé) — la page /shop native de website_sale n'affiche en
# onglets que les catégories de premier niveau (parent_id vide), donc
# les reparenter suffit à les faire disparaître des onglets SANS toucher
# aux produits déjà rattachés (aucune réaffectation nécessaire).
SHOP_CATEGORIES = ['Capsule', 'Cabine', 'Dôme', 'Modulaire', 'Pliable', 'Accessoires']

# Sous-catégories (formats) au sein d'une gamme de premier niveau —
# clé = nom de la catégorie parente (doit être dans SHOP_CATEGORIES),
# valeur = liste des noms d'anciennes/futures catégories enfants.

SHOP_SUBCATEGORIES = {
    'Capsule': ['Studio', 'Duo', 'Panorama'],
}

RESETTABLE_VIEW_XML_IDS = [
    'capsule_house_theme.partial_home_gammes',
    'capsule_house_theme.partial_home_usages',
]



# NOS_MODELES_CATEGORIES (liste figée pour la page /nos-modeles) retirée
# en 19.0.1.0.76 — cette page a été supprimée (demande client : "la page
# nos modèles doit disparaître sur mon code"), la constante n'a donc
# plus aucun consommateur.

# product.attribute utilisé comme simple filtre boutique (pas de vraies
# variantes) : nom -> liste de valeurs.

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