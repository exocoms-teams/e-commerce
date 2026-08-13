# -*- coding: utf-8 -*-
"""
capsule_house_theme — hooks d'installation / maintenance.

Ce module vit sur une base Odoo mutualisée (~17 sites sur la même instance).
Toute la logique ci-dessous respecte les règles de sécurité multi-site :

1. On ne retrouve JAMAIS notre site par son nom (un homonyme peut déjà
   exister). L'id du site créé par CE module est mémorisé dans
   `ir.config_parameter` sous la clé `capsule_house_theme.website_id` et
   c'est le SEUL moyen légitime de le retrouver ensuite.
2. Toute requête sur un modèle scopé site (website.menu, website.page,
   ir.ui.view, product.template, product.public.category...) filtre
   explicitement sur website_id = notre site.
3. Aucune adoption de données orphelines génériques (website_id=False sans
   autre critère strict) ; on filtre toujours aussi par company_id exact,
   jamais de fallback company_id=False.
4. Toute suppression de données de démo est conditionnée à une vérification
   stricte qu'elles sont bien vides/génériques.
5. Chaque fonction est idempotente (get_or_create partout, jamais de
   create() aveugle) : le hook peut être rejoué sans dupliquer ni casser
   l'existant (cron horaire de filet de sécurité + migrations).
6. On logue abondamment à chaque étape ambiguë ou filet de sécurité
   déclenché, pour pouvoir diagnostiquer a posteriori.
"""
import logging

_logger = logging.getLogger(__name__)

from . import controllers
from . import models

CONFIG_WEBSITE_ID_KEY = 'capsule_house_theme.website_id'

# Garde-fou pour _invalidate_frontend_assets() : ce nettoyage ne doit
# tourner qu'UNE SEULE FOIS (pas à chaque passage du cron horaire), voir le
# docstring de cette fonction pour le contexte du bug qu'elle corrige.
CONFIG_ASSETS_FIX_KEY = 'capsule_house_theme.frontend_assets_regenerated_v1'

# Garde-fou pour _set_logo() : appliquer notre logo UNE SEULE FOIS,
# jamais à chaque passage (cron horaire / migration), voir le docstring
# de cette fonction pour le contexte du bug qu'il corrige (website.logo
# déjà non-vide par défaut sur un nouveau site Odoo, donc jamais écrasé
# par l'ancienne condition `if website.logo: return`).
CONFIG_LOGO_APPLIED_KEY = 'capsule_house_theme.logo_applied_v1'
COMPANY_NAME = 'Exocoms Group'
WEBSITE_NAME = 'Capsule House'

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
WEBSITE_DOMAIN = 'capsule-house.fr'
CONFIG_DOMAIN_LIVE_KEY = 'capsule_house_theme.domain_live'

THEME_ASSETS = {
    'variables.css': 'capsule_house_theme/static/src/css/variables.css',
    'base.css': 'capsule_house_theme/static/src/css/base.css',
    'layout.css': 'capsule_house_theme/static/src/css/layout.css',
    'homepage.css': 'capsule_house_theme/static/src/css/homepage.css',
    'shop.css': 'capsule_house_theme/static/src/css/shop.css',
    'odoo-integration.css': 'capsule_house_theme/static/src/css/odoo-integration.css',
    # Ajouté en 19.0.1.0.35 pour la page /avis (voir models/avis.py) :
    # jusque-là réservé/vide pour les futures pages internes (Services,
    # Contact, À propos), désormais utilisé pour de vrai.
    'pages.css': 'capsule_house_theme/static/src/css/pages.css',
    # Ajouté en 19.0.1.0.65 : feuille dédiée aux pages légales
    # (/mentions-legales, /cgv, /confidentialite), jusque-là stylées via
    # les classes .ch-aide-* réutilisées des pages Aide (voir legal.css
    # pour le détail).
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
    # Ajouté en 19.0.1.0.67 (page /nos-modeles, sur le modèle de "Nos
    # services" d'exocoms_theme — voir nos_modeles.xml).
    'capsule_house_theme.page_nos_modeles',
    # Ajoutés en 19.0.1.0.71 (page /nos-gammes : index + détail par
    # gamme, voir nos_gammes.xml et GAMMES_DATA ci-dessus), et section
    # "usages" de l'accueil (remplace l'idée d'une page Application
    # séparée, voir home_usages.xml et USAGES_DATA).
    'capsule_house_theme.page_nos_gammes',
    'capsule_house_theme.page_nos_gammes_detail',
    'capsule_house_theme.partial_home_usages',
    # Ajouté en 19.0.1.0.72 (section gammes de l'accueil, voir
    # home_gammes.xml).
    'capsule_house_theme.partial_home_gammes',
]

# Catégories boutique (product.public.category) reprises de la maquette de
# référence : elles alimentent à la fois le menu (Studio/Duo/Panorama/
# Accessoires) et les pages /shop/category/<id> natives de website_sale.
SHOP_CATEGORIES = ['Studio', 'Duo', 'Panorama', 'Accessoires']

# product.attribute utilisé comme simple filtre boutique (pas de vraies
# variantes) : nom -> liste de valeurs.
SHOP_FILTER_ATTRIBUTES = {
    'Surface (m²)': ['15-20 m²', '20-30 m²', '30-45 m²'],
}

# Gammes de produits (page /nos-gammes, v19.0.1.0.71) — contenu à titre
# informatif, PAS un catalogue transactionnel (demande client : "à titre
# d'information de ce qui sera disponible"). Studio/Duo/Panorama, qui
# vivaient auparavant comme catégories boutique de premier niveau (menu
# + /nos-modeles), sont désormais des FORMATS au sein de la gamme
# "Capsule" (demande client explicite : "studio duo et panorama ne sont
# que les format et accessoire seront les options et équipement").
#
# Statut par gamme :
# - 'disponible' (Capsule) : formats réels déjà publiés ailleurs sur ce
#   site (18 m² Studio / jusqu'à 40 m² Panorama sur /faq), specs/
#   équipements ci-dessous marqués 'indicative'=True (voir note plus bas).
# - 'a_confirmer' (Cabine, Dôme, Modulaire, Pliable) : gammes annoncées
#   par le client mais sans données réelles pour l'instant — listes
#   vides intentionnellement, le template affiche "à définir"/"à
#   confirmer" plutôt que d'inventer des specs.
#
# 'indicative'=True sur Capsule : demande client explicite ("prends en
# compte que les éléments fournis sur capsule-home.fr sont les normes et
# on modifiera plus tard") — les valeurs numériques précises
# (dimensions, kW, matériaux) sont reprises d'un standard du marché, PAS
# des données fournisseur confirmées pour Capsule House. Le template
# affiche un bandeau d'avertissement explicite tant que ce flag est
# True. À repasser à False dès que le fournisseur réel est confirmé.
# Les références de normes (NF EN 1279, NF EN 410, NF EN 14351-1,
# NF C 15-100) sont, elles, de vraies normes françaises vérifiables
# (recherchées le 2026-08-13), pas des valeurs indicatives.
GAMME_STATUS_DISPONIBLE = 'disponible'
GAMME_STATUS_A_CONFIRMER = 'a_confirmer'

GAMMES_DATA = [
    {
        'slug': 'capsule',
        'status': GAMME_STATUS_DISPONIBLE,
        'icon': 'fa-home',
        'name': 'Capsule',
        'indicative': True,
        'tagline_fr': '3 tailles disponibles · 19 à 38 m²',
        'tagline_en': '3 sizes available · 19 to 38 sqm',
        'formats': [
            {'name': 'Studio', 'surface_fr': '19 m²', 'surface_en': '19 sqm',
             'note_fr': 'Compact', 'note_en': 'Compact'},
            {'name': 'Duo', 'surface_fr': '28 m²', 'surface_en': '28 sqm',
             'note_fr': "Jusqu'à 4 pers.", 'note_en': 'Up to 4 people'},
            {'name': 'Panorama', 'surface_fr': '38 m²', 'surface_en': '38 sqm',
             'note_fr': '4 à 6 pers.', 'note_en': '4 to 6 people'},
        ],
        'specs_ext': [
            {'label_fr': 'Façade', 'label_en': 'Facade',
             'value_fr': 'Panneau aluminium', 'value_en': 'Aluminium panel'},
            {'label_fr': "Porte d'entrée", 'label_en': 'Entrance door',
             'value_fr': 'Inox + serrure à code', 'value_en': 'Stainless steel + code lock'},
            {'label_fr': 'Vitrage', 'label_en': 'Glazing',
             'value_fr': 'Vitrage isolant NF EN 1279', 'value_en': 'Insulating glazing NF EN 1279'},
            {'label_fr': 'Fenêtres', 'label_en': 'Windows',
             'value_fr': 'Performances NF EN 14351-1', 'value_en': 'Performance NF EN 14351-1'},
        ],
        'specs_int': [
            {'label_fr': 'Sol principal', 'label_en': 'Main floor',
             'value_fr': 'Revêtement SPC', 'value_en': 'SPC flooring'},
            {'label_fr': 'Électricité', 'label_en': 'Electrical',
             'value_fr': 'Installation NF C 15-100', 'value_en': 'NF C 15-100 wiring'},
            {'label_fr': 'Automatismes', 'label_en': 'Automation',
             'value_fr': 'Store motorisé (option)', 'value_en': 'Motorised blind (option)'},
        ],
        'equipements_fr': [
            'Cadre acier galvanisé', 'Fenêtres double vitrage',
            'Construction isolée et étanche', 'Sanitaire équipé (WC, douche, lavabo)',
            'Installation électrique NF C 15-100', 'Verrouillage sécurisé',
        ],
        'equipements_en': [
            'Galvanised steel frame', 'Double-glazed windows',
            'Insulated, weatherproof construction', 'Equipped bathroom (toilet, shower, sink)',
            'NF C 15-100 electrical wiring', 'Secure locking',
        ],
        'options_fr': ['Chauffage additionnel', 'Isolation renforcée', 'Triple vitrage', 'Aménagement sur mesure'],
        'options_en': ['Additional heating', 'Reinforced insulation', 'Triple glazing', 'Custom fit-out'],
        'usages': ['Logement', 'Bureau', 'Résidence secondaire', 'Location & Airbnb'],
    },
    {
        'slug': 'cabine', 'status': GAMME_STATUS_A_CONFIRMER,
        'icon': 'fa-th-large', 'name': 'Cabine', 'indicative': False,
        'tagline_fr': 'Formats à définir', 'tagline_en': 'Formats to be defined',
        'formats': [], 'specs_ext': [], 'specs_int': [],
        'equipements_fr': [], 'equipements_en': [], 'options_fr': [], 'options_en': [],
        'usages': [],
    },
    {
        'slug': 'dome',
        'status': GAMME_STATUS_A_CONFIRMER,
        'icon': 'fa-circle-o', 'name': 'Dôme', 'indicative': False,
        'tagline_fr': 'Formats à définir', 'tagline_en': 'Formats to be defined',
        'formats': [], 'specs_ext': [], 'specs_int': [],
        'equipements_fr': [], 'equipements_en': [], 'options_fr': [], 'options_en': [],
        'usages': [],
    },
    {
        'slug': 'modulaire',
        'status': GAMME_STATUS_A_CONFIRMER,
        'icon': 'fa-puzzle-piece', 'name': 'Modulaire', 'indicative': False,
        'tagline_fr': 'Système extensible — formats à définir',
        'tagline_en': 'Extensible system — formats to be defined',
        'formats': [], 'specs_ext': [], 'specs_int': [],
        'equipements_fr': [], 'equipements_en': [], 'options_fr': [], 'options_en': [],
        'usages': [],
    },
    {
        'slug': 'pliable',
        'status': GAMME_STATUS_A_CONFIRMER,
        'icon': 'fa-inbox', 'name': 'Pliable', 'indicative': False,
        'tagline_fr': 'Structure repliable — formats à définir',
        'tagline_en': 'Foldable structure — formats to be defined',
        'formats': [], 'specs_ext': [], 'specs_int': [],
        'equipements_fr': [], 'equipements_en': [], 'options_fr': [], 'options_en': [],
        'usages': [],
    },
]

# Usages (section accueil "Trouvez l'usage qui vous correspond", v19.0.1.0.71)
# — remplace l'ancienne idée de page "Application" séparée (demande client :
# "il ne faut plus de page application mais le faire directement sur
# accueil"). Contenu générique et défendable (pas de statistique ni de
# chiffre inventé), inspiré du format de capsule-home.fr mais rédigé pour
# Capsule House — voir échange du 2026-08-13.
USAGES_DATA = [
    {
        'slug': 'logement', 'icon': 'fa-home',
        'name_fr': 'Logement', 'name_en': 'Housing',
        'bullets_fr': [
            'Installation plus rapide qu\'une construction traditionnelle',
            'Autonome sur un petit terrain',
            'Alternative à un achat immobilier classique',
        ],
        'bullets_en': [
            'Faster to install than traditional construction',
            'Self-contained on a small plot',
            'An alternative to a traditional home purchase',
        ],
    },
    {
        'slug': 'bureau', 'icon': 'fa-briefcase',
        'name_fr': 'Bureau', 'name_en': 'Office',
        'bullets_fr': [
            'Espace de travail séparé du logement',
            'Installation indépendante sur votre terrain',
            'Calme et intimité pour se concentrer',
        ],
        'bullets_en': [
            'Work space separate from the home',
            'Standalone installation on your plot',
            'Quiet and private for focused work',
        ],
    },
    {
        'slug': 'residence-secondaire', 'icon': 'fa-sun-o',
        'name_fr': 'Résidence secondaire', 'name_en': 'Second home',
        'bullets_fr': [
            'Installation rapide sur un terrain existant',
            'Entretien réduit par rapport à une maison classique',
            "Utilisable selon l'équipement choisi",
        ],
        'bullets_en': [
            'Quick installation on an existing plot',
            'Less upkeep than a traditional house',
            'Usable depending on the equipment chosen',
        ],
    },
    {
        'slug': 'location-airbnb', 'icon': 'fa-key',
        'name_fr': 'Location & Airbnb', 'name_en': 'Rental & Airbnb',
        'bullets_fr': [
            'Structure autonome et indépendante',
            'Adaptée à la location courte durée',
            'Installation flexible selon le terrain',
        ],
        'bullets_en': [
            'Self-contained, standalone structure',
            'Suited to short-term rental',
            'Flexible installation depending on the plot',
        ],
    },
    {
        'slug': 'accessoires', 'icon': 'fa-wrench',
        'name_fr': 'Accessoires', 'name_en': 'Accessories',
        'bullets_fr': [
            'Personnalisez votre pod selon vos besoins',
            'Ajout possible à la commande',
            'Compatible avec toutes les gammes',
        ],
        'bullets_en': [
            'Customise your pod to your needs',
            'Can be added to your order',
            'Compatible with every range',
        ],
    },
]


def _get_company(env):
    """Retrouve (ou crée) la société Exocoms Group.

    Recherche par nom exact uniquement : les sociétés ne sont pas scopées
    par site, mais on ne veut jamais se raccrocher à une société approchante
    dans la base mutualisée. Si plusieurs correspondances exactes existent
    (ne devrait pas arriver), on logue un avertissement et on prend la
    première par id.
    """
    Company = env['res.company'].sudo()
    companies = Company.search([('name', '=', COMPANY_NAME)], order='id asc')
    if len(companies) > 1:
        _logger.warning(
            "capsule_house_theme: %d sociétés nommées '%s' trouvées, "
            "utilisation de la première (id=%s).",
            len(companies), COMPANY_NAME, companies[0].id,
        )
    if companies:
        return companies[0]

    _logger.info(
        "capsule_house_theme: société '%s' introuvable, création.",
        COMPANY_NAME,
    )
    return Company.create({'name': COMPANY_NAME})


def _grant_company_access(env, company):
    """Ajoute NOTRE société aux sociétés autorisées des administrateurs.

    Bug corrigé (diagnostiqué en conditions réelles via le traceback
    complet de la page d'erreur 403 sur /shop) :

        odoo.exceptions.AccessError: Access to unauthorized or invalid
        companies.
        (levée par la propriété env.companies, odoo/orm/environments.py)

    Ce n'est PAS (contrairement à ce qu'on pensait en 19.0.1.0.14) un
    problème de pricelist manquante en tant que tel : le traceback
    montre que l'erreur remonte de `website_sale.get_pricelist_available()`
    en train de lire `res.country.group.pricelist_ids` (un modèle soumis
    aux règles multi-société), qui a besoin de calculer
    `self.env.companies` pour construire le domaine de sécurité — et ce
    calcul lui-même échoue.

    Cause réelle : quand un administrateur bascule sur le site "Capsule
    House" via le sélecteur de site du backend, Odoo place la société de
    ce site (notre `company`, créée par `_get_company()` ci-dessus) dans
    le contexte de société actif de sa session. Mais si cette société
    n'a jamais été ajoutée aux "sociétés autorisées"
    (`res.users.company_ids`) de cet administrateur, `env.companies`
    lève une AccessError dès qu'un code quelconque a besoin de lire un
    modèle à règle multi-société pendant qu'il navigue sur notre site.

    Fix : ajouter notre société aux sociétés autorisées de tout
    utilisateur membre du groupe Administration/Paramètres
    (`base.group_system`). Cette base mutualisée (~17 sites) est gérée
    par une seule équipe centrale (Exocoms Group) qui administre tous
    les sites clients : il est donc cohérent que ces comptes aient accès
    à chaque société créée par un de leurs propres modules de thème.
    Idempotent : `(4, company.id)` n'ajoute jamais un doublon ; ne
    touche jamais un utilisateur qui n'est pas administrateur système,
    ni les sociétés des autres sites.

    BUG corrigé ici (a fait planter le chargement complet du module en
    conditions réelles — traceback confirmé : `ValueError: Invalid
    field res.users.groups_id`) : le champ many2many `groups_id` sur
    `res.users` a été renommé dans Odoo 19. Plutôt que de deviner/coder
    en dur le nouveau nom (fragile, encore susceptible de changer),
    on utilise `user.has_group(...)`, la méthode stable et publique
    d'Odoo pour tester l'appartenance à un groupe — indépendante du nom
    interne du champ m2m sous-jacent, quelle que soit la version.
    """
    Users = env['res.users'].sudo()
    admin_group_xmlid = 'base.group_system'
    if not env.ref(admin_group_xmlid, raise_if_not_found=False):
        _logger.warning(
            "capsule_house_theme: groupe %s introuvable — accès société "
            "non accordé automatiquement aux administrateurs.",
            admin_group_xmlid,
        )
        return

    # share=False : utilisateurs internes uniquement (exclut portail/
    # public) — champ stable, sert seulement à réduire le volume avant
    # le filtre has_group() ci-dessous, pas de dépendance sur un nom de
    # champ m2m fragile.
    internal_users = Users.search([('share', '=', False)])
    admins = internal_users.filtered(lambda u: u.has_group(admin_group_xmlid))
    updated = []
    for user in admins:
        if company.id not in user.company_ids.ids:
            user.write({'company_ids': [(4, company.id)]})
            updated.append(user.id)
    if updated:
        _logger.info(
            "capsule_house_theme: société '%s' (id=%s) ajoutée aux "
            "sociétés autorisées des administrateurs id=%s — corrige le "
            "403 'Access to unauthorized or invalid companies' rencontré "
            "en naviguant sur /shop depuis le backend.",
            company.name, company.id, updated,
        )


def _get_website(env, company):
    """Retrouve NOTRE site, jamais par nom.

    Règle de sécurité n°1 : un site homonyme "Capsule House" peut déjà
    exister dans la base mutualisée (17 sites dessus). On ne le retrouve
    donc QUE via l'id mémorisé dans ir.config_parameter
    (`capsule_house_theme.website_id`). Si cette clé est absente ou pointe
    vers un site qui n'existe plus, on crée un site tout neuf — on ne
    réutilise JAMAIS un site existant, même en cas d'homonymie parfaite.
    """
    ICP = env['ir.config_parameter'].sudo()
    Website = env['website'].sudo()

    website_id = ICP.get_param(CONFIG_WEBSITE_ID_KEY)
    if website_id:
        try:
            website_id = int(website_id)
        except (TypeError, ValueError):
            website_id = False
        if website_id:
            website = Website.browse(website_id)
            if website.exists():
                return website
            _logger.warning(
                "capsule_house_theme: ir.config_parameter '%s' pointait "
                "vers le site id=%s qui n'existe plus, recréation.",
                CONFIG_WEBSITE_ID_KEY, website_id,
            )

    _logger.info(
        "capsule_house_theme: aucun site mémorisé, création d'un nouveau "
        "site '%s' (jamais de réutilisation par nom).", WEBSITE_NAME,
    )
    website = Website.create({
        'name': WEBSITE_NAME,
        # Pas de 'domain' ici : voir _setup_domain(), qui ne le pose que
        # lorsque le DNS de capsule-house.fr est confirmé en production.
        # Un domaine posé trop tôt casse le sélecteur de site / la preview
        # sur l'environnement de dev/staging (DNS_PROBE_FINISHED_NXDOMAIN).
        'company_id': company.id,
    })
    ICP.set_param(CONFIG_WEBSITE_ID_KEY, str(website.id))
    _logger.info(
        "capsule_house_theme: nouveau site créé id=%s, mémorisé dans '%s'.",
        website.id, CONFIG_WEBSITE_ID_KEY,
    )
    return website


def _setup_pricelist(env, website, company):
    """Garantit qu'une product.pricelist existe pour NOTRE société.

    Bug corrigé (constaté en conditions réelles) : 403 sur /shop —
    "Failed to read field res.country.group.pricelist_ids / Access to
    unauthorized or invalid companies."

    Cause : `_get_company()` crée notre société via un simple
    `res.company.create({'name': ...})`. Contrairement à la création
    d'une société via l'assistant standard d'Odoo (Paramètres >
    Sociétés), un `create()` direct ne seed AUCUNE pricelist par défaut
    pour cette société. Sans pricelist scopée à notre company_id,
    website_sale élargit sa recherche de pricelist applicable via les
    groupes de pays partagés (`res.country.group.pricelist_ids`) — une
    liste qui traverse TOUTES les pricelists de la base mutualisée, y
    compris celles des ~16 autres sociétés/sites, que la nôtre n'est pas
    autorisée à lire (règle d'accès multi-société native d'Odoo) : d'où
    le 403.

    Fix : créer une pricelist scopée strictement à NOTRE company_id (et
    à aucune autre), pour qu'Odoo la trouve directement sans jamais
    avoir besoin d'élargir sa recherche à d'autres sociétés. Idempotent :
    recherche filtrée sur company_id = notre société avant de créer, ne
    lit/écrit jamais une pricelist appartenant à une autre société.
    """
    Pricelist = env['product.pricelist'].sudo()
    pricelist = Pricelist.search([('company_id', '=', company.id)], limit=1)
    if not pricelist:
        vals = {'name': 'Capsule House - Tarif public', 'company_id': company.id}
        if 'currency_id' in Pricelist._fields and company.currency_id:
            vals['currency_id'] = company.currency_id.id
        pricelist = Pricelist.create(vals)
        _logger.info(
            "capsule_house_theme: pricelist créée pour la société '%s' "
            "(company_id=%s, pricelist_id=%s) — corrige le 403 sur /shop "
            "causé par l'absence de pricelist scopée à notre société.",
            company.name, company.id, pricelist.id,
        )

    # Champ de pricelist par défaut du site : le nom exact varie selon la
    # version/le mode multi-pricelist activé (feature-detect, comme
    # ailleurs dans ce module, plutôt que de supposer un nom de champ).
    Website = env['website']
    for field_name in ('pricelist_id', 'default_pricelist_id'):
        if field_name in Website._fields and not website[field_name]:
            website.write({field_name: pricelist.id})
            _logger.info(
                "capsule_house_theme: website.%s posé sur la pricelist "
                "id=%s pour le site id=%s.", field_name, pricelist.id, website.id,
            )
            break


def _get_default_operator(env):
    """Retourne un utilisateur RÉEL (jamais OdooBot/système) pour servir
    d'opérateur par défaut du Live Chat — même correctif que
    exocoms_theme._get_default_operator() : `env.uid` pointe vers
    OdooBot (id=1, compte système inactif) quand ce code s'exécute via
    un hook/cron plutôt qu'une vraie session utilisateur, ce qui
    laisserait le canal sans opérateur valide (donc invisible) après
    chaque install/rebuild si on s'y fiait.
    """
    return env['res.users'].search([
        ('active', '=', True),
        ('share', '=', False),
        ('login', 'not in', ['__system__']),
    ], order='id asc', limit=1)


def _setup_livechat(env, website):
    """Crée (ou retrouve) un canal Live Chat dédié à NOTRE site et le
    rattache via website.channel_id — champ nativement scopé par site
    (chaque website a son propre channel_id), donc aucun risque de fuite
    vers un autre site de la base mutualisée avec ce mécanisme.

    Réplique le mécanisme observé sur exocoms_theme._setup_livechat(),
    avec une différence délibérée : le canal est nommé d'après
    WEBSITE_NAME ('Capsule House'), PAS COMPANY_NAME ('Exocoms Group').
    COMPANY_NAME est la société PARTAGÉE par les ~17 sites de cette
    base (Exocoms Group gère tous les sites clients) — un canal
    recherché par ce nom risquerait de retrouver/réutiliser le canal
    d'un AUTRE site déjà installé avec le même COMPANY_NAME (dont
    exocoms_theme lui-même), et donc de repeindre son widget avec nos
    couleurs ou de mélanger ses règles d'affichage avec les nôtres.
    Un nom distinct par site garantit l'isolation.
    """
    if not website:
        return
    channel_name = '%s - Live Chat' % WEBSITE_NAME
    channel = env['im_livechat.channel'].search([
        ('name', '=', channel_name),
    ], limit=1)
    if not channel:
        channel = env['im_livechat.channel'].create({'name': channel_name})
    if website.channel_id.id != channel.id:
        website.write({'channel_id': channel.id})

    # Couleurs du widget alignées sur notre palette (--ch-terracotta /
    # --ch-ink dans variables.css), plutôt que la couleur par défaut
    # (ou celle d'exocoms) d'un canal créé par code.
    channel.write({
        'header_background_color': '#1F2421',
        'title_color': '#FFFFFF',
        'button_background_color': '#C1694F',
        'button_text_color': '#FFFFFF',
    })

    # Un canal créé par code (.create()) n'a AUCUNE règle d'affichage
    # (im_livechat.channel.rule) par défaut — contrairement à un canal
    # créé depuis l'interface. Sans règle, Odoo ne sait sur quelles
    # pages afficher la bulle de chat, donc elle n'apparaît nulle part.
    if not channel.rule_ids:
        env['im_livechat.channel.rule'].create({
            'channel_id': channel.id,
            'regex_url': '/',
            'action': 'display_button',
            'sequence': 10,
        })

    # Réassigne un opérateur RÉEL si le canal n'en a aucun, à chaque
    # exécution (install ET update), pas seulement à la création —
    # sinon un canal existant mais resté sans opérateur valide (ex:
    # après un rebuild) reste invisible tant qu'on ne le corrige pas
    # manuellement.
    if not channel.user_ids:
        operator = _get_default_operator(env)
        if operator:
            channel.write({'user_ids': [(4, operator.id)]})
            _logger.info(
                "capsule_house_theme: opérateur Live Chat assigné "
                "automatiquement : %s.", operator.name,
            )
        else:
            _logger.warning(
                "capsule_house_theme: aucun utilisateur actif trouvé "
                "pour servir d'opérateur Live Chat — la bulle de chat "
                "pourrait ne pas s'afficher. Assignez un opérateur "
                "manuellement via Site Web > Live Chat."
            )


def _setup_languages(env, website):
    """Active fr_FR + en_US sur le site et fixe fr_FR comme langue par
    défaut — même pattern que exocoms_theme._setup_languages().

    GAP repéré lors de l'audit systématique contre exocoms_theme (le
    client a demandé qu'on regarde son module de référence de bout en
    bout plutôt qu'au coup par coup) : le header (header.xml/layout.css)
    affiche déjà un sélecteur de langue natif, mais UNIQUEMENT si
    `len(request.website.language_ids) > 1` — sans cette fonction, rien
    dans ce module n'activait jamais de deuxième langue sur le site.
    Le sélecteur de langue demandé par le client restait donc construit
    mais invisible, comme si on ne l'avait jamais livré.

    Idempotent : ne réactive pas une langue déjà active, ne réécrase pas
    `language_ids`/`default_lang_id` s'ils sont déjà corrects. Rejouable
    depuis le cron horaire comme le reste de run_theme_maintenance (même
    remarque que exocoms_theme : sans extraction en fonction séparée
    rejouée à chaque passage, une perte de configuration — ex. site
    dupliqué depuis un snapshot antérieur — ne serait plus jamais
    corrigée automatiquement).
    """
    lang_fr = env['res.lang'].search([('code', '=', 'fr_FR')], limit=1)
    if not lang_fr:
        env['res.lang']._activate_lang('fr_FR')
        lang_fr = env['res.lang'].search([('code', '=', 'fr_FR')], limit=1)

    lang_en = env['res.lang'].search([('code', '=', 'en_US')], limit=1)
    if not lang_en:
        env['res.lang']._activate_lang('en_US')
        lang_en = env['res.lang'].search([('code', '=', 'en_US')], limit=1)

    if not (website and lang_fr):
        return

    wanted_ids = {lang_fr.id} | ({lang_en.id} if lang_en else set())
    current_ids = set(website.language_ids.ids)
    if website.default_lang_id.id != lang_fr.id or current_ids != wanted_ids:
        website.write({
            'default_lang_id': lang_fr.id,
            'language_ids': [(6, 0, list(wanted_ids))],
        })
        _logger.info(
            "capsule_house_theme: langues du site id=%s synchronisées "
            "(fr_FR par défaut%s) — active le sélecteur de langue natif "
            "du header.", website.id, ' + en_US' if lang_en else '',
        )


def _reload_native_translations(env):
    """Recharge les traductions françaises OFFICIELLES d'Odoo pour les
    modules natifs utilisés par le header/portail — même pattern que
    exocoms_theme (__init__.py, appelé depuis leur post_init_hook).

    Retour client : "tu vois ça ne suit pas la langue" — capture du
    menu déroulant du compte natif (icône profil) affichant "My
    Account" / "Logout" en ANGLAIS alors que le site est en français
    (sélecteur de langue sur "Français"). Ce menu n'est PAS un template
    à nous : c'est le dropdown natif Odoo du module `portal`
    (`portal.user_dropdown_link_account` et consorts, déjà référencé
    dans `_remove_account_dropdown_duplicate` plus bas). Sur une base
    mutualisée où le français a pu être activé après coup sur certains
    modules, les traductions officielles de ces chaînes natives
    peuvent ne jamais avoir été chargées en base pour fr_FR — d'où le
    repli sur l'anglais par défaut malgré une langue de site correcte.

    Sans danger : ne fait qu'installer/rafraîchir des fichiers de
    traduction officiels Odoo (aucune donnée business, aucune config),
    et se limite volontairement aux modules natifs concernés (mêmes
    noms que chez exocoms) plutôt qu'à TOUS les modules installés sur
    cette base mutualisée à ~17 sites — inutile et plus lent de
    recharger les traductions de modules sans rapport avec ce thème.
    """
    try:
        mods = env['ir.module.module'].search([
            ('name', 'in', [
                'base', 'web', 'website', 'website_sale',
                'portal', 'auth_signup', 'mail', 'sale',
            ]),
            ('state', '=', 'installed'),
        ])
        mods._update_translations('fr_FR')
        _logger.info(
            "capsule_house_theme: traductions fr_FR rechargées pour %d "
            "module(s) natif(s) (menu compte, portail...).", len(mods),
        )
    except Exception:
        _logger.exception(
            "capsule_house_theme: échec rechargement traductions fr_FR "
            "des modules natifs."
        )


LOGO_PATH = ('static', 'src', 'img', 'capsule-house-logo.png')


def _set_logo(env, website):
    """Pose le logo du site — même pattern que exocoms_theme._set_logo().

    Le header natif Odoo (header#top, voir README "Header natif comme sur
    exocoms_theme") affiche le logo via `.navbar-brand.logo img`, dont la
    source est le champ natif `website.logo` : on ne peut plus injecter
    notre propre SVG décoratif dans le DOM (ce serait recréer un header
    custom, exactement ce qu'on vient de corriger). Il faut donc que ce
    champ pointe vers notre image de marque.

    `capsule-house-logo.png` = le badge SVG validé par le client (repris
    tel quel de l'ancien header.xml, cf. commentaire dans ce fichier) +
    le wordmark "capsule house", aplatis en un seul PNG (rasterisé une
    fois, stocké en asset statique du module).

    BUG corrigé ici (constaté en conditions réelles : le header affichait
    le placeholder générique Odoo "Your Logo" au lieu du nôtre) : la
    condition précédente `if website.logo: return` supposait que
    website.logo était vide par défaut sur un site neuf. En réalité Odoo
    pose lui-même une valeur par défaut (placeholder) sur ce champ à la
    création du site, donc cette condition empêchait TOUJOURS notre pose,
    même au tout premier passage du hook. Remplacé par un garde-fou
    ir.config_parameter classique (même idiome que
    CONFIG_ASSETS_FIX_KEY) : on force la pose UNE SEULE FOIS, ce qui
    écrase bien le placeholder Odoo initial, sans jamais revenir écraser
    un changement fait volontairement en backend après coup.
    """
    ICP = env['ir.config_parameter'].sudo()
    if ICP.get_param(CONFIG_LOGO_APPLIED_KEY) == '1':
        return
    try:
        import base64
        import os
        logo_path = os.path.join(os.path.dirname(__file__), *LOGO_PATH)
        if os.path.exists(logo_path):
            with open(logo_path, 'rb') as f:
                website.write({'logo': base64.b64encode(f.read())})
            ICP.set_param(CONFIG_LOGO_APPLIED_KEY, '1')
            _logger.info("capsule_house_theme: logo appliqué au site id=%s.", website.id)
        else:
            _logger.warning(
                "capsule_house_theme: %s introuvable — site id=%s laissé "
                "avec le logo par défaut Odoo pour l'instant (le hook "
                "réessaiera au prochain passage, la clé de garde n'est "
                "posée qu'en cas de succès réel).",
                os.path.join(*LOGO_PATH), website.id,
            )
    except Exception:
        _logger.exception(
            "capsule_house_theme: échec non bloquant lors de la pose du logo "
            "sur le site id=%s.", website.id,
        )


def _setup_homepage(env, website):
    """Nettoie `website.homepage_url` : l'accueil est servi DIRECTEMENT
    sur '/' depuis la 19.0.1.0.57 (voir `CapsuleHouseWebsite.index()`
    dans controllers/main.py), plus via un redirect vers une route
    dédiée. Un `homepage_url` resté à l'ancienne valeur
    (`/capsule-house/home`) n'aurait pas d'effet fonctionnel pour nos
    visiteurs (notre `index()` intercepte '/' avant que le mécanisme
    natif de redirect ne s'applique), mais on le vide quand même pour
    rester cohérent avec exocoms_theme (qui ne pose jamais ce champ) et
    éviter tout signal SEO/sitemap trompeur. Idempotent : simple write,
    sans effet si déjà vide.

    CAUSE DE CE CHANGEMENT (19.0.1.0.57, analyse complète des deux
    thèmes) : le redirect natif '/' -> homepage_url était un vrai
    aller-retour HTTP (confirmé par capture DevTools client), qui
    empêchait le Website Builder de marquer la section hero de
    l'accueil comme un bloc sélectionnable (panneau Style vide), alors
    que le même hero sur /avis (servie en un seul rendu, sans redirect)
    fonctionnait normalement. Voir migrations/19.0.1.0.57/.
    """
    if website.homepage_url:
        _logger.info(
            "capsule_house_theme: homepage_url du site id=%s vidée "
            "(était %r) — l'accueil est servi directement sur '/' "
            "depuis la 19.0.1.0.57.", website.id, website.homepage_url,
        )
        website.write({'homepage_url': False})


def _setup_domain(env, website):
    """Ne pose `website.domain` que si le DNS est confirmé en production.

    Un `domain` posé sur le site avant que le DNS de capsule-house.fr ne
    pointe réellement vers cette instance casse le sélecteur de site et la
    preview dans le backend (Odoo essaie de rediriger vers ce domaine —
    NXDOMAIN sur un environnement de dev/staging). Ce module ne pose donc
    le domaine que si `ir.config_parameter`
    (`capsule_house_theme.domain_live`) vaut explicitement '1' — à activer
    manuellement le jour où le DNS est confirmé.

    Idempotent et corrige aussi une éventuelle valeur posée par erreur lors
    d'une version antérieure de ce hook (rejoué par le cron horaire /
    post-migrate) : si le domaine vaut encore notre valeur par défaut alors
    que le DNS n'est pas confirmé, on le vide pour restaurer la preview.
    """
    domain_live = env['ir.config_parameter'].sudo().get_param(CONFIG_DOMAIN_LIVE_KEY)
    if domain_live == '1':
        if website.domain != WEBSITE_DOMAIN:
            website.write({'domain': WEBSITE_DOMAIN})
            _logger.info(
                "capsule_house_theme: domaine %s confirmé (DNS live), posé "
                "sur le site id=%s.", WEBSITE_DOMAIN, website.id,
            )
        return

    if website.domain == WEBSITE_DOMAIN:
        website.write({'domain': False})
        _logger.warning(
            "capsule_house_theme: domaine %s retiré du site id=%s — DNS "
            "pas confirmé (%s absent/différent de '1'). Sélecteur de "
            "site/preview restaurés. Mettre ce paramètre à '1' une fois le "
            "DNS réellement en place.", WEBSITE_DOMAIN, website.id,
            CONFIG_DOMAIN_LIVE_KEY,
        )


def _setup_website_priority(env, website):
    """Donne à NOTRE site la priorité (sequence basse) dans le
    départage natif Odoo entre sites candidats, sans domaine posé.

    Contexte du bug (v19.0.1.0.43) : retour client capture à l'appui —
    en cliquant "Déconnexion", l'utilisateur atterrissait sur le site
    Odoo générique par défaut ("My Website" — logo placeholder, menu
    Home/Shop/Contact us) au lieu de rester sur Capsule House, alors
    que la page d'accueil (`/`) résolvait, elle, correctement vers
    Capsule House sur la même URL. Diagnostic mené EN LISANT LE CODE
    (pas en modifiant quoi que ce soit sur l'instance) : `/web/login`
    et `/web/session/logout` sont des routes natives Odoo qui ne
    passent pas par le même mécanisme de résolution "site courant" que
    les pages de contenu — sans `website.domain` posé (notre cas tant
    que le DNS n'est pas confirmé, voir `_setup_domain()` ci-dessus),
    Odoo les départage entre sites candidats via `website.sequence`
    (plus bas = prioritaire), pas par nom d'hôte.

    Vérifié en lisant les enregistrements `website` réels d'une autre
    base (exocoms_theme, à titre de comparaison) : tous les sites
    partagent la même `sequence` par défaut (10) posée par Odoo à la
    création — rien dans LEUR code ne la modifie non plus (recherche
    exhaustive dans exocoms_theme : aucune occurrence de `sequence`
    sur le modèle `website`, aucune route de login/logout personnalisée).
    Le comportement qu'on cherche à obtenir n'est donc pas une astuce
    qu'ils auraient codée et qu'on aurait ratée — c'est un réglage à
    poser nous-mêmes, ici, pour NOTRE site.

    Fix : poser `website.sequence` à une valeur strictement plus basse
    que la valeur par défaut (10) partagée par tous les sites non
    configurés (dont le site générique "My Website"), pour que Capsule
    House gagne systématiquement ce départage — y compris sur les
    routes natives comme `/web/login`/`/web/session/logout`. Portée
    strictement limitée à NOTRE enregistrement website (jamais touché
    ailleurs), donc sans risque pour les autres sites de la base.
    Idempotent : no-op si déjà posé.
    """
    if website.sequence >= 10:
        website.write({'sequence': 1})
        _logger.info(
            "capsule_house_theme: sequence du site id=%s abaissée à 1 "
            "(était %s) — priorité sur le site générique par défaut "
            "pour les routes natives sans résolution par domaine "
            "(/web/login, /web/session/logout...).",
            website.id, website.sequence,
        )


def _setup_theme_assets(env, website):
    """Enregistre le CSS/JS du thème via ir.asset, scopé à NOTRE site.

    Règle de sécurité clé : ce module ne doit JAMAIS injecter ses fichiers
    dans web.assets_frontend (bundle global partagé par les ~17 sites de la
    base), sous peine de repeindre les autres sites avec nos variables CSS
    (--primary, --secondary, etc.). On crée donc des ir.asset avec
    website_id posé explicitement sur notre site, get_or_create par
    (name, website_id) pour rester idempotent.
    """
    IrAsset = env['ir.asset'].sudo()
    for label, path in THEME_ASSETS.items():
        name = 'capsule_house_theme: %s' % label
        bundle = 'web.assets_frontend'
        directive = 'append'
        existing = IrAsset.search([
            ('name', '=', name),
            ('website_id', '=', website.id),
        ], limit=1)
        vals = {
            'name': name,
            'bundle': bundle,
            'directive': directive,
            'path': path,
            'website_id': website.id,
            'sequence': 16,
        }
        if existing:
            existing.write(vals)
        else:
            IrAsset.create(vals)
    _logger.info(
        "capsule_house_theme: %d assets (ir.asset) enregistrés pour le "
        "site id=%s uniquement.", len(THEME_ASSETS), website.id,
    )


def _invalidate_frontend_assets(env, website):
    """Force la régénération du bundle web.assets_frontend de NOTRE site.

    Contexte du bug corrigé : diagnostic navigateur (DevTools) confirmé —
    la balise <link> réelle chargée par la page ne parse que 2 règles CSS
    (les @import Google Fonts) alors qu'une requête brute sur la même URL
    renvoie le fichier complet et correct (nos règles .ch-* y sont bien).
    Signe d'un ir.attachment de bundle compilé une fois de façon
    incomplète/corrompue (probablement un timeout de compilation SCSS sur
    l'environnement dev.odoo.com) et resservi tel quel tant que son hash de
    cache ne change pas — un simple rechargement navigateur ne corrige donc
    rien, il faut changer le hash côté serveur.

    On supprime les `ir.attachment` du bundle compilé pour NOTRE site
    uniquement (filtré sur `/web/assets/<website.id>/` ET sur le nom du
    bundle `web.assets_frontend`) : Odoo les régénère automatiquement,
    sous un nouveau hash, au prochain chargement de page. Comme ce bundle
    est mutualisé (~17 sites sur la même base), on ne le fait qu'UNE FOIS
    (garde via ir.config_parameter) pour ne pas forcer une recompilation en
    boucle à chaque passage du cron horaire.
    """
    ICP = env['ir.config_parameter'].sudo()
    if ICP.get_param(CONFIG_ASSETS_FIX_KEY) == '1':
        return

    Attachment = env['ir.attachment'].sudo()
    stale = Attachment.search([
        ('url', 'like', '/web/assets/%s/' % website.id),
        ('url', 'like', 'web.assets_frontend'),
    ])
    if stale:
        _logger.warning(
            "capsule_house_theme: suppression de %d ir.attachment de bundle "
            "web.assets_frontend potentiellement corrompu(s) pour le site "
            "id=%s (%s) — régénération forcée sous un nouveau hash au "
            "prochain chargement de page.",
            len(stale), website.id, stale.mapped('name'),
        )
        stale.unlink()
    else:
        _logger.info(
            "capsule_house_theme: aucun ir.attachment de bundle "
            "web.assets_frontend trouvé pour le site id=%s (rien à "
            "régénérer, ou pas encore compilé).", website.id,
        )
    ICP.set_param(CONFIG_ASSETS_FIX_KEY, '1')


def _scope_layout_views(env, website):
    """Force website_id sur les vues livrées par ce module.

    Sans cette étape, les ir.ui.view créées par les données XML du module
    (header, footer, layout, pages) ont website_id=False et s'appliqueraient
    par défaut à TOUS les sites de la base mutualisée, pas seulement au
    nôtre. On les repasse explicitement sur notre website_id, en ciblant
    chaque vue par son external id connu — jamais par une recherche large
    sur ir.ui.view.
    """
    View = env['ir.ui.view'].sudo()
    scoped, missing = 0, []
    for xml_id in SCOPED_VIEW_XML_IDS:
        view = env.ref(xml_id, raise_if_not_found=False)
        if not view:
            missing.append(xml_id)
            continue
        if view.website_id.id != website.id:
            view.write({'website_id': website.id})
            scoped += 1
    if missing:
        _logger.warning(
            "capsule_house_theme: vues attendues introuvables (pas encore "
            "livrées ?) : %s", missing,
        )
    _logger.info(
        "capsule_house_theme: %d vue(s) scopée(s) sur website_id=%s.",
        scoped, website.id,
    )


def _clean_demo_data(env, website):
    """Supprime un éventuel site fantôme homonyme, seulement s'il est vide.

    Filet de sécurité pour le cas où une install précédente (ou une
    initialisation Odoo standard) aurait créé un site "Capsule House" en
    plus du nôtre. On ne supprime CE site fantôme que s'il n'a aucun produit
    et au maximum 1 page (critère strict de site générique/vide) — jamais
    s'il contient le moindre contenu réel. Notre propre site (retrouvé par
    id mémorisé) n'est bien sûr jamais concerné.
    """
    Website = env['website'].sudo()
    candidates = Website.search([
        ('name', '=', WEBSITE_NAME),
        ('id', '!=', website.id),
    ])
    if not candidates:
        return

    for ghost in candidates:
        product_count = env['product.template'].sudo().search_count([
            ('website_id', '=', ghost.id),
        ])
        page_count = env['website.page'].sudo().search_count([
            ('website_id', '=', ghost.id),
        ])
        if product_count == 0 and page_count <= 1:
            _logger.warning(
                "capsule_house_theme: suppression du site fantôme id=%s "
                "('%s', %d produit(s), %d page(s)) — critère vide respecté.",
                ghost.id, ghost.name, product_count, page_count,
            )
            ghost.unlink()
        else:
            _logger.warning(
                "capsule_house_theme: site homonyme id=%s détecté mais NON "
                "supprimé (%d produit(s), %d page(s) — pas considéré vide). "
                "Vérification manuelle recommandée.",
                ghost.id, product_count, page_count,
            )


def _setup_shop_categories(env, website):
    """Crée les catégories boutique (Studio, Duo, Panorama, Accessoires).

    Alimente à la fois le menu de nav (_setup_menus) et les pages
    /shop/category/<id> natives de website_sale. `product.public.category`
    n'a pas systématiquement de champ `website_id` selon la version d'Odoo
    (feature-detect ci-dessous) : quand il existe, on le pose explicitement
    pour respecter la règle de scope site ; sinon on logue un avertissement
    car la catégorie sera alors une taxonomie partagée par la base
    mutualisée (comportement natif Odoo dans ce cas, pas une erreur de ce
    module).

    Retourne un dict {nom: record} pour construction des URLs de menu.
    """
    Category = env['product.public.category'].sudo()
    has_website_field = 'website_id' in Category._fields
    if not has_website_field:
        _logger.warning(
            "capsule_house_theme: product.public.category n'a pas de champ "
            "website_id sur cette version d'Odoo — catégories créées comme "
            "taxonomie globale, non scopée par site."
        )

    categories = {}
    for name in SHOP_CATEGORIES:
        domain = [('name', '=', name)]
        if has_website_field:
            domain += ['|', ('website_id', '=', website.id), ('website_id', '=', False)]
        category = Category.search(domain, limit=1)
        if category:
            if has_website_field and not category.website_id:
                category.write({'website_id': website.id})
        else:
            vals = {'name': name}
            if has_website_field:
                vals['website_id'] = website.id
            category = Category.create(vals)
        categories[name] = category
    _logger.info(
        "capsule_house_theme: %d catégorie(s) boutique synchronisée(s) "
        "pour le site id=%s.", len(categories), website.id,
    )
    return categories


SHOP_DESIGN_CLASSES = (
    # v19.0.1.0.41 — retour client : "je t'ai dit que je voulais ce
    # design [Chips] sur mes produits du shop, essaye de voir comment
    # ça a été fait sur exocoms_theme pour bien le faire sur Capsule
    # House". La liste précédente ici était DEVINÉE (mauvaise
    # supposition : "Chips" = o_wsale_products_opt_design_thumbs, +
    # rounded_2, actions_onhover, wishlist_fixed, has_description,
    # actions_subtle — aucune de ces classes ne vient du vrai design
    # Chips). Remplacée par la liste EXACTE lue dans le code réel
    # d'exocoms_theme (__init__.py, écrite deux fois : post_init_hook
    # et le hook de maintenance principal — confirmée fonctionnelle en
    # production sur leur site, pas devinée). La classe qui porte
    # vraiment le nom "Chips" est o_wsale_products_opt_design_chips.
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


def _setup_shop_display(env, website):
    """Pose le design "Chips" de la grille boutique — EN CODE, pas via un
    clic dans l'éditeur de site (demande explicite du client : "je veux
    ça mais je veux que ça soit en local").

    Odoo stocke ce réglage nativement sur des champs du modèle `website`
    (pas une vue séparée à hériter) : `shop_opt_products_design_classes`
    (la chaîne de classes CSS qui pilote le design "Chips"/"Grid"/
    "List" — la classe qui porte vraiment le nom "Chips" est
    `o_wsale_products_opt_design_chips`), plus `shop_ppg`/`shop_ppr`/
    `shop_gap` (taille de grille), `shop_page_container` et
    `shop_default_sort`.

    SHOP_DESIGN_CLASSES (v19.0.1.0.41) : liste EXACTE reprise du code
    réel d'exocoms_theme (leur __init__.py, écrite dans post_init_hook
    ET dans le hook de maintenance principal), pas devinée — voir le
    commentaire sur SHOP_DESIGN_CLASSES ci-dessus pour le détail des
    classes précédemment fausses. `_setup_shop_grid_design()` (appelée
    juste après) est un filet de sécurité repris de la même logique
    chez eux : si Odoo a déjà créé une vue `website_sale.products`
    spécifique à NOTRE site (website_id posé), on s'assure que sa vue
    QWeb porte bien la classe `o_wsale_products_opt_design_chips` sur
    le conteneur grid, au cas où le simple champ `website.write()`
    ne suffise pas à lui seul. On ne crée JAMAIS cette vue nous-mêmes
    et on ne touche JAMAIS à la vue générique partagée par les 17
    sites de la base — exactement la même prudence que sur
    _setup_shop_grid_design() côté exocoms.

    Valeurs de grille reprises telles quelles depuis l'état actuel du
    site (confirmé en lisant les vrais champs en conditions réelles,
    pas deviné) : grille 21 produits par page, 3 colonnes, écart 16px,
    conteneur "regular", tri par défaut "En vedette"
    (`website_sequence asc`). Idempotent : simple write si une valeur
    diffère de celle voulue, sans quoi ce serait un no-op à chaque
    passage du cron horaire.
    """
    Website = env['website']
    wanted = {
        'shop_ppg': 21,
        'shop_ppr': 3,
        'shop_gap': '16px',
        'shop_page_container': 'regular',
        'shop_opt_products_design_classes': SHOP_DESIGN_CLASSES,
        'shop_default_sort': 'website_sequence asc',
    }
    to_write = {}
    for field_name, value in wanted.items():
        if field_name in Website._fields and website[field_name] != value:
            to_write[field_name] = value
    if to_write:
        website.write(to_write)
        _logger.info(
            "capsule_house_theme: design boutique (Chips) posé sur le "
            "site id=%s (%s).", website.id, list(to_write.keys()),
        )


def _setup_shop_grid_design(env, website):
    """Filet de sécurité pour le design "Chips" de la grille boutique —
    repris tel quel (même prudence de scoping) de la fonction du même
    nom dans exocoms_theme.

    `_setup_shop_display()` pose déjà `shop_opt_products_design_classes`
    sur le modèle `website`, ce qui suffit dans la quasi-totalité des
    cas. Mais si Odoo a créé une vue QWeb `website_sale.products`
    spécifique à NOTRE site (website_id posé — typiquement après une
    personnalisation faite une fois dans l'éditeur de site), cette vue
    peut porter sa propre classe sur le conteneur grid, indépendamment
    du champ `website`. On s'assure alors que `o_wsale_products_opt_
    design_chips` y est bien présente aussi.

    Scoping STRICT, leçon apprise chez exocoms (leur propre commentaire
    documente un bug corrigé : la version originale cherchait TOUTES
    les vues `website_sale.products` de la base sans filtre de site, et
    modifiait donc potentiellement la vue générique partagée par les
    17 sites) : on ne cherche QUE les vues avec `website_id = notre
    site`, et si aucune n'existe on ne touche À RIEN — pas question de
    créer nous-mêmes une vue spécifique ni de modifier la vue globale.
    """
    try:
        grid_views = env['ir.ui.view'].search([
            ('key', 'like', 'website_sale.products'),
            ('type', '=', 'qweb'),
            ('website_id', '=', website.id),
        ])
        if not grid_views:
            _logger.info(
                "capsule_house_theme: aucune vue 'website_sale.products' "
                "spécifique au site id=%s — design Chips posé uniquement "
                "via le champ website (pas de vue dédiée à corriger).",
                website.id,
            )
            return
        for grid_view in grid_views:
            try:
                arch = grid_view.arch
                if 'o_wsale_products_grid' in arch and \
                   'o_wsale_products_opt_design_chips' not in arch:
                    if 'o_wsale_products_opt_layout_catalog' in arch:
                        arch = arch.replace(
                            'o_wsale_products_opt_layout_catalog',
                            'o_wsale_products_opt_layout_catalog'
                            ' o_wsale_products_opt_design_chips'
                        )
                    elif 'o_wsale_products_grid_table grid' in arch:
                        arch = arch.replace(
                            'o_wsale_products_grid_table grid',
                            'o_wsale_products_grid_table grid'
                            ' o_wsale_products_opt_design_chips'
                        )
                    grid_view.write({'arch': arch})
                    _logger.info(
                        "capsule_house_theme: classe design Chips "
                        "ajoutée sur la vue id=%s (site id=%s).",
                        grid_view.id, website.id,
                    )
            except Exception:
                _logger.exception(
                    "capsule_house_theme: échec application design "
                    "Chips sur vue id=%s.", grid_view.id,
                )
    except Exception:
        _logger.exception(
            "capsule_house_theme: échec recherche des vues grid "
            "produits (site id=%s).", website.id,
        )


def _setup_menus(env, website, categories):
    """Crée le menu du site, scopé à notre website_id.

    Reprend la nav de la maquette de référence : Accueil, Tous les pods
    (/shop), une entrée par catégorie boutique, puis Promotions.
    get_or_create par (url, website_id) pour rester idempotent et ne
    jamais dupliquer une entrée au fil des rejeux du hook / du cron.

    Accueil pointe vers '/' (depuis la 19.0.1.0.57 — l'accueil est
    servi directement sur '/', voir CapsuleHouseWebsite.index() dans
    controllers/main.py, plus de redirect via homepage_url/
    HOMEPAGE_ROUTE). Historique du bug corrigé en 19.0.1.0.19-ish
    (indicateur "page active" du header absent sur "Accueil") : à
    l'époque, `/` faisait un redirect natif Odoo vers
    `website.homepage_url` (= HOMEPAGE_ROUTE), donc l'URL réellement
    affichée dans le navigateur différait de celle du menu — corrigé
    alors en pointant le menu directement sur HOMEPAGE_ROUTE. Depuis
    la 19.0.1.0.57, ce redirect n'existe plus (index() sert '/'
    directement, sans aller-retour) : l'URL réelle de l'accueil est de
    nouveau '/', donc le menu y pointe de nouveau aussi — la
    comparaison reste exacte.
    """
    Menu = env['website.menu'].sudo()
    entries = [
        ('Accueil', '/', 10),
        # Nos gammes (/nos-gammes) et Nos modèles (/nos-modeles) retirées
        # des entrées de menu du header en 19.0.1.0.72 (demande client :
        # "enlève nos modèle et nos gamme sur le header") — leur contenu
        # est désormais visible directement sur l'accueil (voir
        # home_gammes.xml / home_usages.xml). Les deux pages et leurs
        # routes existent toujours (accessibles via l'accueil et les
        # liens croisés), simplement plus référencées dans la nav
        # principale.
        ('Tous les pods', '/shop', 20),
    ]
    sequence = 30
    # Studio/Duo/Panorama retirés des entrées de menu par catégorie
    # (19.0.1.0.71, voir commentaire ci-dessus) : seule Accessoires
    # reste une entrée directe, car ce n'est pas une gamme (options et
    # équipements, pas un format de pod) — les catégories
    # product.public.category elles-mêmes restent inchangées (toujours
    # nécessaires pour /shop/category/<id> et le rattachement produits).
    if 'Accessoires' in categories:
        entries.append((
            'Accessoires', '/shop/category/%d' % categories['Accessoires'].id, sequence,
        ))
        sequence += 10
    # Pas de route de filtre "promotions" native dans website_sale : ce lien
    # pointe sur /shop pour l'instant. À remplacer par une vraie route
    # filtrée (ex: domaine sur les prix barrés / une pricelist promo) une
    # fois le mécanisme de promotion du client confirmé.
    entries.append(('Promotions', '/shop?promotions=1', sequence))
    sequence += 10
    # Page /avis (capsule.house.avis, voir models/avis.py) : vrais avis
    # clients, modérés avant publication.
    entries.append(('Avis clients', '/avis', sequence))

    # Traduction EN du libellé de menu (v19.0.1.0.37) : `website.menu.name`
    # est un champ traduisible nativement dans Odoo, mais rien ne posait
    # jamais de valeur pour en_US — d'où le nav resté français même une
    # fois la langue du site basculée en anglais (retour client explicite).
    # Studio/Duo/Panorama ne sont pas traduits : ce sont des noms de
    # gammes de produits (comme des noms propres), pas du texte d'UI —
    # cohérent avec le choix de ne jamais traduire les noms de produits.
    # 'Nos gammes' / 'Nos modèles' retirées de ce dict en 19.0.1.0.72 (plus
    # d'entrée de menu correspondante, voir `entries` ci-dessus) — les
    # libellés EN de ces deux pages vivent maintenant directement dans
    # nos_gammes.xml / nos_modeles.xml (t-set="title" par page).
    EN_MENU_NAMES = {
        'Accueil': 'Home',
        'Tous les pods': 'All pods',
        'Promotions': 'Deals',
        'Avis clients': 'Reviews',
        'Accessoires': 'Accessories',
    }

    known_urls = {url for _, url, _ in entries}
    kept_menu_ids = set()
    for name, url, seq in entries:
        existing = Menu.search([
            ('url', '=', url),
            ('website_id', '=', website.id),
        ], limit=1)
        # Bug réel trouvé en v.38 (inspection live, page confirmée en
        # français) : le menu s'affichait en ANGLAIS alors que le
        # sélecteur de langue était sur "Français". Cause : l'écriture
        # du libellé français ci-dessous n'imposait aucun contexte de
        # langue, donc héritait de la langue ambiante de l'environnement
        # du hook/cron (superuser, en_US par défaut) — le texte français
        # atterrissait dans la case de traduction "en_US", que l'écriture
        # EN explicite juste après écrasait avec "Home" etc. La case
        # "fr_FR" n'était donc JAMAIS remplie, et un visiteur FR se
        # rabattait sur la valeur en_US. Fix : poser fr_FR explicitement
        # des deux côtés (write ET create), jamais compter sur la langue
        # ambiante de l'env.
        if existing:
            existing.with_context(lang='fr_FR').write({'name': name, 'sequence': seq})
            record = existing
        else:
            record = Menu.with_context(lang='fr_FR').create({
                'name': name,
                'url': url,
                'sequence': seq,
                'website_id': website.id,
                'parent_id': website.menu_id.id,
            })
        kept_menu_ids.add(record.id)
        if record.with_context(lang='fr_FR').name != name:
            record.with_context(lang='fr_FR').write({'name': name})
        en_name = EN_MENU_NAMES.get(name)
        if en_name and record.with_context(lang='en_US').name != en_name:
            record.with_context(lang='en_US').write({'name': en_name})
    _logger.info(
        "capsule_house_theme: menu du site id=%s synchronisé (%d entrées).",
        website.id, len(entries),
    )

    # Odoo pré-remplit automatiquement un menu par défaut (ex: "Contact
    # Us") à la création de tout nouveau site — jamais nettoyé ailleurs.
    # On retire ici tout enfant DIRECT de notre menu racine qui ne fait pas
    # partie de notre nav définie ci-dessus, en se limitant strictement aux
    # menus scopés sur website_id = le nôtre (jamais touché sur un autre
    # site) et de premier niveau (pas de sous-menus imbriqués par d'autres
    # modules).
    stray_menus = website.menu_id.child_id.filtered(
        lambda m: m.id not in kept_menu_ids and m.url not in known_urls
    )
    if stray_menus:
        # v19.0.1.0.62 : passé de warning à info — suppression attendue et
        # idempotente (menu par défaut d'Odoo type "Contact Us", jamais une
        # anomalie), ne devrait pas remonter comme un signal d'alerte côté
        # Odoo.sh (voir README "Warning Odoo.sh récurrent").
        _logger.info(
            "capsule_house_theme: suppression de %d menu(s) par défaut non "
            "reconnu(s) sur le site id=%s : %s.",
            len(stray_menus), website.id, stray_menus.mapped('name'),
        )
        stray_menus.unlink()


def _setup_shop_filters(env):
    """Crée les attributs produit utilisés comme filtres boutique.

    Toujours en create_variant='no_variant' : ce sont des filtres de
    navigation, pas de vraies variantes produit. On protège la création
    par un try/except : si l'attribut existe déjà ailleurs dans la base
    mutualisée en mode variante réelle (utilisé par un autre site/produit),
    on logue et on continue sans planter l'install.
    """
    Attribute = env['product.attribute'].sudo()
    for attr_name, values in SHOP_FILTER_ATTRIBUTES.items():
        try:
            attribute = Attribute.search([('name', '=', attr_name)], limit=1)
            if not attribute:
                attribute = Attribute.create({
                    'name': attr_name,
                    'create_variant': 'no_variant',
                    'display_type': 'select',
                })
            elif attribute.create_variant != 'no_variant':
                _logger.warning(
                    "capsule_house_theme: l'attribut '%s' existe déjà en "
                    "mode '%s' (probablement utilisé par un autre site sur "
                    "la base mutualisée) — laissé tel quel, pas de filtre "
                    "boutique appliqué dessus.",
                    attr_name, attribute.create_variant,
                )
                continue

            existing_values = set(attribute.value_ids.mapped('name'))
            for value_name in values:
                if value_name not in existing_values:
                    env['product.attribute.value'].sudo().create({
                        'name': value_name,
                        'attribute_id': attribute.id,
                    })
        except Exception:
            _logger.exception(
                "capsule_house_theme: échec non bloquant lors de la "
                "création de l'attribut filtre '%s'.", attr_name,
            )


def _attach_shop_filters_to_products(env, website):
    """Rattache l'attribut filtre 'Surface (m²)' aux produits publiés.

    Leçon tirée telle quelle du module de référence exocoms_theme
    (_attach_monetique_attributes_to_products) : Odoo n'affiche un filtre
    dans la sidebar boutique QUE pour un attribut effectivement porté par
    au moins un produit affiché (product.template.attribute_line_ids).
    _setup_shop_filters() ci-dessus ne crée que le catalogue global
    (product.attribute / product.attribute.value) — sans ce rattachement,
    le filtre 'Surface (m²)' resterait invisible côté boutique bien
    qu'existant en base, exactement le bug documenté et corrigé une
    première fois dans exocoms_theme.

    Appelée volontairement APRÈS _publish_our_products() dans
    run_theme_maintenance() : il faut que les produits soient déjà
    scopés à notre website_id et publiés pour être trouvés ici.

    Idempotent : ne retouche jamais un produit qui a déjà une ligne pour
    cet attribut (ne réécrase jamais une sélection de valeurs déjà
    affinée manuellement en backend). Filet de sécurité : ignore tout
    attribut qui ne serait plus en mode 'no_variant' (cf. le même filet
    dans _setup_shop_filters) pour ne jamais provoquer une explosion de
    variantes en le rattachant tel quel.
    """
    Attribute = env['product.attribute'].sudo()
    Product = env['product.template'].sudo()
    for attr_name in SHOP_FILTER_ATTRIBUTES:
        attribute = Attribute.search([('name', '=', attr_name)], limit=1)
        if not attribute or not attribute.value_ids:
            continue
        if attribute.create_variant != 'no_variant':
            _logger.warning(
                "capsule_house_theme: attribut filtre '%s' pas en mode "
                "'no_variant' — rattachement aux produits ignoré (voir le "
                "même garde-fou dans _setup_shop_filters).", attr_name,
            )
            continue

        products = Product.search([
            ('website_id', '=', website.id),
            ('is_published', '=', True),
        ])
        attached = 0
        for product in products:
            existing_attr_ids = set(product.attribute_line_ids.mapped('attribute_id').ids)
            if attribute.id in existing_attr_ids:
                continue
            product.write({'attribute_line_ids': [
                (0, 0, {
                    'attribute_id': attribute.id,
                    'value_ids': [(6, 0, attribute.value_ids.ids)],
                }),
            ]})
            attached += 1
        if attached:
            _logger.info(
                "capsule_house_theme: attribut filtre '%s' rattaché à %d "
                "produit(s) du site id=%s (filtre désormais visible côté "
                "boutique).", attr_name, attached, website.id,
            )
        else:
            _logger.info(
                "capsule_house_theme: attribut filtre '%s' déjà rattaché à "
                "tous les produits pertinents du site id=%s (rien à faire).",
                attr_name, website.id,
            )


def _publish_our_products(env, website, company):
    """Publie sur NOTRE site les produits de NOTRE société uniquement.

    Filtre strict sur company_id = notre société exacte (jamais de fallback
    company_id=False) et website_id qui est soit déjà le nôtre, soit vide
    (produit pas encore rattaché à un site). On ne touche jamais aux
    produits d'une autre company_id, même si website_id est vide.
    """
    Product = env['product.template'].sudo()
    products = Product.search([
        ('company_id', '=', company.id),
        '|',
        ('website_id', '=', False),
        ('website_id', '=', website.id),
    ])
    if not products:
        _logger.info(
            "capsule_house_theme: aucun produit trouvé pour la société "
            "'%s' à publier sur le site id=%s pour l'instant.",
            company.name, website.id,
        )
        return
    products.write({
        'website_id': website.id,
        'is_published': True,
    })
    _logger.info(
        "capsule_house_theme: %d produit(s) de '%s' publié(s) sur le site "
        "id=%s.", len(products), company.name, website.id,
    )


def run_theme_maintenance(env):
    """Point d'entrée unique, rejouable, de toute la logique du thème.

    Appelé par post_init_hook (install/update) ET par le cron horaire
    (capsule.house.theme.maintenance) qui sert de filet de sécurité
    indépendant du versioning des migrations. Chaque étape est idempotente.
    """
    company = _get_company(env)
    _grant_company_access(env, company)
    website = _get_website(env, company)
    _setup_pricelist(env, website, company)
    _setup_languages(env, website)
    _reload_native_translations(env)
    _set_logo(env, website)
    _setup_homepage(env, website)
    _setup_domain(env, website)
    _setup_website_priority(env, website)
    _setup_theme_assets(env, website)
    _invalidate_frontend_assets(env, website)
    _scope_layout_views(env, website)
    _setup_livechat(env, website)
    _clean_demo_data(env, website)
    categories = _setup_shop_categories(env, website)
    _setup_shop_display(env, website)
    _setup_shop_grid_design(env, website)
    _setup_menus(env, website, categories)
    _setup_shop_filters(env)
    _publish_our_products(env, website, company)
    _attach_shop_filters_to_products(env, website)
    _logger.info(
        "capsule_house_theme: run_theme_maintenance terminé (website_id=%s, "
        "company_id=%s).", website.id, company.id,
    )
    return website


def post_init_hook(env):
    """Hook d'installation Odoo standard.

    Signature `(env)` : depuis Odoo 17, les hooks pre_init/post_init/
    uninstall reçoivent directement un `api.Environment`, plus `(cr,
    registry)` comme avant. Ce module cible Odoo 19 (voir __manifest__.py),
    d'où cette signature.
    """
    run_theme_maintenance(env)
