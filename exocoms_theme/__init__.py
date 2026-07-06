# -*- coding: utf-8 -*-
import base64
import logging

from odoo.tools import file_path

from . import controllers
from . import models

_logger = logging.getLogger(__name__)

WEBSITE_NAME = 'Exocoms'
COMPANY_NAME = 'Exocoms Group'
MODULE_NAME = 'exocoms_theme'  # <-- adaptez si le nom réel du module diffère
LOGO_PATH = ('static', 'src', 'img', 'EXOCOMS.png')
OUR_URLS = ['/', '/shop', '/nos-services']
THEME_CSS_FILES = [
    'exocoms_theme/static/src/css/layout.css',
    'exocoms_theme/static/src/css/header.css',
    'exocoms_theme/static/src/css/hero.css',
    'exocoms_theme/static/src/css/features.css',
    'exocoms_theme/static/src/css/products.css',
    'exocoms_theme/static/src/css/footer.css',
    'exocoms_theme/static/src/css/categories.css',
    'exocoms_theme/static/src/css/cta.css',
    'exocoms_theme/static/src/css/dashbord.css',
    'exocoms_theme/static/src/css/dashbord_boutique.css',
    'exocoms_theme/static/src/css/services_content.css',
    'exocoms_theme/static/src/css/services_features.css',
    'exocoms_theme/static/src/css/services_hero.css',
    'exocoms_theme/static/src/css/home.css',
    'exocoms_theme/static/src/css/legal.css',
    'exocoms_theme/static/src/css/animations.css',
    'exocoms_theme/static/src/css/benefits.css',
    'exocoms_theme/static/src/css/cards.css',
    'exocoms_theme/static/src/css/pages.css',
    'exocoms_theme/static/src/css/sections.css',
    'exocoms_theme/static/src/css/home_sections.css',
    'exocoms_theme/static/src/css/odoo-integration.css',
    'exocoms_theme/static/src/css/responsive.css',
    'https://cdnjs.cloudflare.com/ajax/libs/font-awesome/6.4.0/css/all.min.css',    # toujours en dernier
]
THEME_JS_FILES = [
    'exocoms_theme/static/src/js/main.js',
]


def _get_website(env):
    """Retourne LE site qui appartient à CE module — jamais un autre
    site préexistant, même s'il porte exactement le même nom
    ('Exocoms'). C'est le cas ici : un site nommé 'Exocoms' existe
    déjà dans la base partagée avant même l'installation du module.

    CORRECTIF MAJEUR : l'ancienne version cherchait le site PAR NOM
    ('=ilike', WEBSITE_NAME) — donc elle retombait systématiquement
    sur ce site préexistant et fusionnait nos données dedans (origine
    de tous les conflits de catégories/produits qu'on a dû corriger
    à la main). Désormais, on mémorise l'ID exact du site créé par CE
    module dans un paramètre système (ir.config_parameter). À chaque
    lancement suivant (update, rebuild...), on ne retrouve QUE ce
    site précis par son ID — jamais par une recherche de nom qui
    pourrait accidentellement matcher le site de quelqu'un d'autre.

    Si le paramètre est absent (première installation, ou base neuve
    après un rebuild) OU si l'enregistrement qu'il pointe n'existe
    plus, un site TOUT NEUF est créé — jamais réutilisé depuis un
    site existant, même en cas d'homonymie parfaite.
    """
    param_key = 'exocoms_theme.website_id'
    params = env['ir.config_parameter'].sudo()
    stored_id = params.get_param(param_key)

    if stored_id:
        website = env['website'].browse(int(stored_id))
        if website.exists():
            return website
        _logger.warning(
            "Le paramètre '%s' pointait vers un site (id=%s) qui "
            "n'existe plus — création d'un nouveau site.",
            param_key, stored_id,
        )

    # Aucun site connu, ou son ID ne correspond plus à rien -> on en
    # crée un NOUVEAU, sans JAMAIS réutiliser un site préexistant,
    # même s'il porte exactement le même nom.
    website = env['website'].create({'name': WEBSITE_NAME})
    params.set_param(param_key, str(website.id))
    _logger.info(
        "Nouveau site Exocoms créé (id=%s), totalement indépendant de "
        "tout autre site préexistant portant potentiellement le même nom.",
        website.id,
    )
    return website


def _get_company(env):
    """Retourne la société Exocoms Group — par nom, jamais par défaut.
    Ne touche JAMAIS à une société existante qui ne nous appartient pas
    (base partagée avec d'autres projets) : si absente, on la CRÉE
    plutôt que de prendre la première société trouvée."""
    company = env['res.company'].search([('name', '=ilike', COMPANY_NAME)], limit=1)
    if not company:
        company = env['res.company'].create({'name': COMPANY_NAME})
    return company


def _set_logo(env, website):
    """Applique le logo Exocoms UNIQUEMENT sur notre site (jamais sur
    'website.default_website', qui pointe vers le premier site de la
    base et peut appartenir à un autre projet client)."""
    if not website:
        return
    try:
        logo_path = file_path(f'{MODULE_NAME}/{"/".join(LOGO_PATH)}', filter_ext=('.png',))
        if logo_path:
            with open(logo_path, 'rb') as f:
                website.write({'logo': base64.b64encode(f.read())})
    except FileNotFoundError:
        _logger.warning("Logo Exocoms introuvable à static/src/img/EXOCOMS.png — site %s non modifié", website.name)
    except Exception:
        _logger.exception("Impossible d'appliquer le logo Exocoms sur le site %s", website.name)


def _setup_theme_assets(env, website):
    """CORRECTIF MAJEUR (cause du bug 'le style/header apparaît sur
    tous les sites') : les CSS/JS étaient chargés via le manifest
    dans 'web.assets_frontend', un bundle GLOBAL à toute la base
    Odoo, jamais filtré par site. Résultat : le `:root{...}` de
    layout.css (variables --primary, --secondary...) repeignait
    silencieusement TOUS les sites, car ces noms de variables sont
    aussi utilisés par les thèmes natifs Odoo pour boutons/liens.

    On utilise désormais `ir.asset` avec `website_id` posé : Odoo ne
    chargera ces fichiers QUE sur les pages du site Exocoms."""
    if not website:
        return
    Asset = env['ir.asset']
    for path in THEME_CSS_FILES + THEME_JS_FILES:
        existing = Asset.search([
            ('path', '=', path),
            ('website_id', '=', website.id),
        ], limit=1)
        if not existing:
            Asset.create({
                'name': f'Exocoms - {path}',
                'bundle': 'web.assets_frontend',
                'path': path,
                'directive': 'append',
                'website_id': website.id,
            })


def _scope_layout_views(env, website):
    """CORRECTIF : custom_footer et custom_copyright héritent de
    website.layout (gabarit universel) sans website_id -> ils
    s'appliquaient à TOUS les sites. On les rattache explicitement
    au site Exocoms uniquement."""
    if not website:
        return
    keys = [
        'exocoms_theme.custom_footer',
        'exocoms_theme.custom_copyright',
        'exocoms_theme.boutique_seo',
    ]
    views = env['ir.ui.view'].search([('key', 'in', keys)])
    for v in views:
        if not v.website_id:
            v.write({'website_id': website.id})


def _clean_demo_data(env, website):
    """Nettoie les données de démo créées automatiquement par Odoo.
    - Supprime "My Website 2" (site fantôme de démo), SI ET SEULEMENT SI
      ce site n'a aucune page/menu/produit réel (sécurité supplémentaire
      sur base multi-sites : on ne veut jamais supprimer un site client
      qui porterait accidentellement ce nom).
    - Supprime les doublons de menus sur notre site UNIQUEMENT.
    """
    if not website:
        return

    # 1. Supprimer le site fantôme de démo Odoo — ciblé par nom exact,
    #    ET seulement s'il est vide (sécurité ajoutée pour base partagée
    #    avec 17 sites : on ne veut jamais détruire un vrai site client
    #    qui porterait ce nom par coïncidence).
    ghost = env['website'].search([
        ('name', '=', 'My Website 2'),
        ('id', '!=', website.id),
    ], limit=1)
    if ghost:
        ghost_menus = env['website.menu'].search([('website_id', '=', ghost.id)])
        ghost_pages = env['website.page'].search([('website_id', '=', ghost.id)])
        ghost_products = env['product.template'].search([('website_id', '=', ghost.id)])
        # On ne supprime que si ça ressemble vraiment à un site de démo
        # vide (pas de produits, peu/pas de pages personnalisées).
        if not ghost_products and len(ghost_pages) <= 1:
            ghost_menus.unlink()
            ghost_pages.unlink()
            ghost.unlink()
        else:
            _logger.warning(
                "Site 'My Website 2' trouvé mais NON supprimé : il contient "
                "des données (produits=%s, pages=%s) — ne ressemble pas à "
                "un site de démo vide. Vérification manuelle recommandée.",
                len(ghost_products), len(ghost_pages),
            )

    # CORRECTIF (analyse a posteriori — bloc supprimé) : ce point
    # contenait auparavant un rattachement automatique de "menus
    # orphelins" (website_id=False) dont l'URL correspondait à
    # OUR_URLS ('/', '/shop', '/nos-services'). Ce filtre était une
    # fausse sécurité : ces URLs sont génériques (page d'accueil et
    # boutique standard de N'IMPORTE QUEL site e-commerce Odoo), pas
    # spécifiques à Exocoms. Sans filtre de site sur le search(), ce
    # bloc pouvait potentiellement s'approprier le menu "Accueil" ou
    # "Boutique" d'un AUTRE site de la base partagée, si celui-ci se
    # retrouvait temporairement orphelin (migration, bug, manipulation
    # d'une autre équipe...). Il tournait en plus à CHAQUE update du
    # module (post_migrate_hook), donc le risque n'était pas ponctuel.
    # SUPPRIMÉ : totalement inutile de toute façon, puisque
    # _get_or_create_menu() (appelée juste après dans _setup_menus)
    # crée déjà le menu proprement, scopé à website.id, s'il n'existe
    # pas encore — aucune perte de fonctionnalité.

    # Supprimer les doublons de menus sur notre site
    # Garder uniquement le menu avec la sequence la plus basse pour chaque URL
    for url in OUR_URLS:
        menus = env['website.menu'].search([
            ('url', '=', url),
            ('website_id', '=', website.id),
        ], order='sequence asc')
        if len(menus) > 1:
            menus[1:].unlink()


def _get_or_create_menu(env, url, name_fr, name_en, sequence, website, root_menu, lang_en):
    """Crée ou met à jour un menu par URL — jamais par ID."""
    domain = [('url', '=', url), ('website_id', '=', website.id)]
    menu = env['website.menu'].search(domain, limit=1)
    if not menu:
        vals = {
            'url': url,
            'name': name_fr,
            'sequence': sequence,
            'website_id': website.id,
        }
        if root_menu:
            vals['parent_id'] = root_menu.id
        menu = env['website.menu'].create(vals)
    else:
        menu.write({'url': url, 'sequence': sequence})

    # Nom traduit séparément — URL jamais dans un contexte langue
    menu.with_context(lang='fr_FR').write({'name': name_fr})
    if lang_en:
        menu.with_context(lang='en_US').write({'name': name_en})
    return menu


def _setup_menus(env, website, lang_en):
    """Gestion complète des menus — strictement scopée à website.id."""
    if not website:
        return

    # Nettoyer d'abord les données de démo et doublons
    _clean_demo_data(env, website)

    root_menu = env['website.menu'].search([
        ('parent_id', '=', False),
        ('website_id', '=', website.id),
    ], limit=1)

    menus = [
        ('/',             'Accueil',      'Home',         1),
        ('/shop',         'Boutique',     'Shop',         2),
        ('/nos-services', 'Nos services', 'Our Services', 3),
    ]
    for url, name_fr, name_en, seq in menus:
        _get_or_create_menu(env, url, name_fr, name_en, seq, website, root_menu, lang_en)

    # Supprimer les menus indésirables sur notre site uniquement
    unwanted_urls = ['/contactus', '/blog', '/forum', '/event', '/jobs', '/slides']
    unwanted = env['website.menu'].search([
        ('url', 'in', unwanted_urls),
        ('website_id', '=', website.id),
    ])
    if unwanted:
        unwanted.unlink()

    # CORRECTIF MAJEUR (cause du bug "menus d'autres sites affichés") :
    # le bloc original captait TOUT menu orphelin restant sous l'hypothèse
    # fausse "on n'a qu'un seul site". Sur une base à 17 sites, ce bloc
    # aspirait des menus appartenant à d'autres projets (Events, Courses,
    # Appointment, Jobs...). SUPPRIMÉ : on ne rattache plus que ce qui
    # est explicitement connu (OUR_URLS, déjà géré par _clean_demo_data).


def _setup_monetique_attributes(env, lang_en):
    """Crée les attributs/filtres boutique pour la gamme Monétique.

    NOTE multi-sites : product.attribute et product.attribute.value sont
    des modèles GLOBAUX dans Odoo (pas de website_id) — ils sont par
    nature partagés entre tous les sites de la base, ce qui est normal
    et sans danger ici : un attribut "Garantie" peut être réutilisé par
    n'importe quel produit, quel que soit son site. Le risque
    multi-sites ne se situe pas dans cette fonction.
    """
    attr_model = env['product.attribute']
    value_model = env['product.attribute.value']

    def get_or_create_attribute(name_fr, name_en, display_type='radio', sequence=10):
        attr = attr_model.with_context(lang='fr_FR').search(
            [('name', '=', name_fr)], limit=1
        )
        if not attr:
            attr = attr_model.with_context(lang='fr_FR').create({
                'name': name_fr,
                'display_type': display_type,
                'create_variant': 'no_variant',
                'sequence': sequence,
            })
        else:
            attr.with_context(lang='fr_FR').write({'sequence': sequence})

        attr.with_context(lang='fr_FR').write({'name': name_fr})
        if lang_en and name_en:
            attr.with_context(lang='en_US').write({'name': name_en})
        return attr

    def get_or_create_value(attribute, name_fr, name_en, sequence=10):
        val = value_model.with_context(lang='fr_FR').search([
            ('name', '=', name_fr),
            ('attribute_id', '=', attribute.id),
        ], limit=1)
        if not val:
            val = value_model.with_context(lang='fr_FR').create({
                'name': name_fr,
                'attribute_id': attribute.id,
                'sequence': sequence,
            })
        else:
            val.with_context(lang='fr_FR').write({'sequence': sequence})

        val.with_context(lang='fr_FR').write({'name': name_fr})
        if lang_en and name_en:
            val.with_context(lang='en_US').write({'name': name_en})
        return val

    forfait = get_or_create_attribute(
        'Forfait DATA par TPE', 'TPE Data Plan',
        display_type='radio', sequence=1
    )
    for i, (fr, en) in enumerate([
        ('5 Mo', '5 MB'),
        ('50 Mo', '50 MB'),
        ('100 Mo', '100 MB'),
    ]):
        get_or_create_value(forfait, fr, en, sequence=i)

    cheques = get_or_create_attribute(
        'Nombre de chèques par mois', 'Cheques per month',
        display_type='select', sequence=2
    )
    for i, (fr, en) in enumerate([
        ('5', '5'), ('10', '10'), ('15', '15'),
        ('20', '20'), ('30', '30'), ('50', '50'),
    ]):
        get_or_create_value(cheques, fr, en, sequence=i)

    garantie = get_or_create_attribute(
        'Garantie', 'Warranty',
        display_type='radio', sequence=3
    )
    for i, (fr, en) in enumerate([
        ('1an', '1 year'),
        ('2ans', '2 years'),
        ('3ans', '3 years'),
        ('4ans', '4 years'),
    ]):
        get_or_create_value(garantie, fr, en, sequence=i)

    modele = get_or_create_attribute(
        'Type de modèle', 'Model type',
        display_type='select', sequence=4
    )
    for i, (fr, en) in enumerate([
        ('1 x RS232', '1 x RS232'),
        ('2 x RS232', '2 x RS232'),
    ]):
        get_or_create_value(modele, fr, en, sequence=i)

    quantite = get_or_create_attribute(
        'Quantité', 'Quantity',
        display_type='pills', sequence=5
    )
    for i, (fr, en) in enumerate([
        ('5', '5'), ('15', '15'), ('20', '20'), ('50', '50'),
    ]):
        get_or_create_value(quantite, fr, en, sequence=i)


def _remove_account_dropdown_duplicate(env, website):
    """CORRECTIF : cette fonction créait auparavant un lien "My Account"
    en double dans le menu déroulant du compte client, en plus du lien
    natif "Mon compte" déjà fourni par Odoo (portail) — les deux
    pointaient vers la même page (/my/home). Doublon inutile et
    source de confusion pour le visiteur, présent dès la toute
    première version du module.

    On retire ici cette vue custom si elle existe (scopée à notre
    site uniquement), pour ne garder que le lien natif d'Odoo.
    Idempotent : ne fait rien si la vue a déjà été retirée.
    """
    if not website:
        return
    account_view = env['ir.ui.view'].search([
        ('key', '=', 'portal.user_dropdown_link_account'),
        ('website_id', '=', website.id),
    ], limit=1)
    if account_view:
        account_view.unlink()
        _logger.info(
            "Vue custom 'My Account' (doublon) retirée sur le site %s.",
            website.name,
        )


def _setup_shop_grid_design(env, website):
    """CORRECTIF MAJEUR : la version originale cherchait TOUTES les vues
    'website_sale.products' qweb de la base SANS filtre de site, donc
    modifiait potentiellement la vue générique partagée par les 17
    sites de la base. On ne modifie désormais QUE la vue déjà
    spécifique à notre site (website_id = website.id). Si elle n'existe
    pas encore, on ne touche à RIEN — il faut d'abord l'activer
    manuellement via Site Web > Personnaliser sur le site Exocoms, ce
    qui crée automatiquement la vue spécifique avec website_id posé
    correctement par Odoo lui-même.
    """
    try:
        grid_views = env['ir.ui.view'].search([
            ('key', 'like', 'website_sale.products'),
            ('type', '=', 'qweb'),
            ('website_id', '=', website.id),
        ])
        if not grid_views:
            _logger.info(
                "Aucune vue 'website_sale.products' spécifique au site "
                "Exocoms (website_id=%s) — design 'chips' non appliqué "
                "pour éviter de modifier la vue partagée par les autres "
                "sites. Activez une personnalisation sur ce site via "
                "Site Web > Personnaliser, puis relancez le module.",
                website.id,
            )
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
            except Exception:
                _logger.exception("Échec application design chips sur vue id=%s", grid_view.id)
    except Exception:
        _logger.exception("Échec recherche des vues grid produits")


def _publish_our_products(env, website, company):
    """CORRECTIF MAJEUR : la version originale publiait TOUS les
    produits non publiés de TOUTE la base sur le site Exocoms — y
    compris des brouillons appartenant à d'autres sites/sociétés. On
    restreint maintenant strictement aux produits qui n'ont AUCUN site
    assigné (orphelins) ET qui appartiennent à notre société (ou à
    aucune société, en mono-société) — jamais aux produits déjà
    rattachés à un autre website_id.
    """
    try:
        domain = [
            ('is_published', '=', False),
            ('website_id', '=', False),  # jamais un produit déjà sur un autre site
        ]
        if company:
            domain.append(('company_id', 'in', [company.id, False]))
        products = env['product.template'].search(domain)
        if products:
            products.write({
                'is_published': True,
                'website_id': website.id,
            })
    except Exception:
        _logger.exception("Échec publication des produits Exocoms")


def _merge_root_category(env, website, old_name, target_category):
    """RÉCUPÈRE une ancienne catégorie racine préexistante (nom
    différent de la nôtre, ex: 'Informatique') en migrant TOUS ses
    produits vers notre catégorie cible (ex: 'Informatique & Réseaux').
    Rien n'est perdu : chaque produit garde ses catégories existantes
    ET gagne la nouvelle. L'ancienne catégorie racine est ensuite
    archivée (active=False) pour qu'elle disparaisse du filmstrip —
    mais elle n'est jamais supprimée, et reste réactivable si besoin.
    """
    if not website or not target_category:
        return
    old = env['product.public.category'].search([
        ('name', '=', old_name),
        ('website_id', '=', website.id),
        ('parent_id', '=', False),
    ], limit=1)
    if not old or old.id == target_category.id:
        return
    products = env['product.template'].search([
        ('public_categ_ids', 'in', old.id),
    ])
    for p in products:
        new_categs = (p.public_categ_ids - old) | target_category
        p.write({'public_categ_ids': [(6, 0, new_categs.ids)]})
    old.write({'active': False})
    _logger.info(
        "Catégorie '%s' (id=%s) RÉCUPÉRÉE dans '%s' : %s produit(s) "
        "migré(s), rien perdu. Ancienne catégorie archivée "
        "(active=False, jamais supprimée).",
        old_name, old.id, target_category.name, len(products),
    )


def _publish_category_tree_products(env, website, category):
    """Publie tous les produits rattachés à une catégorie ET à ses
    sous-catégories (récursif). Corrige le cas où les PRODUITS d'une
    catégorie récupérée (ex: Crypto, Distributeur automatique,
    Informatique) restent marqués 'Non publié' individuellement
    (product.template.is_published) — NOTE : product.public.category
    n'a pas de champ de publication propre sur cette version d'Odoo
    (contrairement à une fausse hypothèse initiale qui a causé une
    erreur d'installation, cf. 'Invalid field website_published').
    Seuls les PRODUITS ont un statut de publication, pas les
    catégories elles-mêmes.

    Ne touche JAMAIS un produit déjà explicitement rattaché à un
    AUTRE site (website_id différent) — sécurité multi-sites."""
    if not category or not website:
        return
    tree = category | env['product.public.category'].search([
        ('id', 'child_of', category.ids),
    ])
    products = env['product.template'].search([
        ('public_categ_ids', 'in', tree.ids),
    ])
    updated = 0
    for p in products:
        vals = {}
        if not p.is_published:
            vals['is_published'] = True
        if not p.website_id:
            vals['website_id'] = website.id
        elif p.website_id.id != website.id:
            # Produit déjà scopé à un AUTRE site — on n'y touche jamais.
            continue
        if vals:
            p.write(vals)
            updated += 1
    if updated:
        _logger.info(
            "%s produit(s) publié(s) sous la catégorie '%s' (et ses sous-catégories).",
            updated, category.name,
        )


def _get_default_operator(env):
    """Retourne un utilisateur RÉEL (jamais OdooBot/système) pour
    servir d'opérateur par défaut du Live Chat.

    CORRECTIF : l'ancienne version utilisait env.uid, qui pointe vers
    OdooBot (id=1, compte système INACTIF) quand le code s'exécute
    via odoo-bin shell — c'est exactement pour ça que l'opérateur
    restait vide après chaque installation/rebuild, obligeant à le
    corriger manuellement à chaque fois. On cherche ici explicitement
    un utilisateur actif, interne (non "share", donc pas un simple
    contact portail), en excluant les comptes techniques.
    """
    return env['res.users'].search([
        ('active', '=', True),
        ('share', '=', False),
        ('login', 'not in', ['__system__']),
    ], order='id asc', limit=1)


def _setup_livechat(env, website):
    """Crée (ou retrouve) un canal Live Chat dédié à Exocoms Group et
    le rattache à NOTRE site uniquement, via website.channel_id — un
    champ déjà nativement scopé par site dans Odoo (chaque website a
    son propre channel_id), donc aucun risque de fuite vers un autre
    site avec ce mécanisme, contrairement au CSS/footer qu'on a dû
    corriger manuellement plus haut dans ce fichier.
    """
    if not website:
        return
    channel = env['im_livechat.channel'].search([
        ('name', '=', COMPANY_NAME),
    ], limit=1)
    if not channel:
        channel = env['im_livechat.channel'].create({'name': COMPANY_NAME})
    if website.channel_id.id != channel.id:
        website.write({'channel_id': channel.id})

    # Couleurs du widget alignées sur le bleu principal du site
    # (--primary: #0d4dff dans layout.css), plutôt que la couleur
    # aléatoire/violette par défaut d'un canal créé par code.
    channel.write({
        'header_background_color': '#0d4dff',
        'title_color': '#FFFFFF',
        'button_background_color': '#0d4dff',
        'button_text_color': '#FFFFFF',
    })

    # CORRECTIF : un canal créé par code (.create()) n'a AUCUNE règle
    # d'affichage (im_livechat.channel.rule) par défaut — contrairement
    # à un canal créé depuis l'interface, qui en crée une
    # automatiquement. Sans règle, Odoo ne sait sur quelles pages
    # afficher la bulle de chat, donc elle n'apparaît nulle part. On
    # ajoute une règle simple : afficher le bouton sur toutes les
    # pages du site.
    if not channel.rule_ids:
        env['im_livechat.channel.rule'].create({
            'channel_id': channel.id,
            'regex_url': '/',
            'action': 'display_button',
            'sequence': 10,
        })

    # CORRECTIF : réassigne un opérateur RÉEL à CHAQUE exécution
    # (install ET update) si le canal n'en a aucun — pas seulement à
    # la création. Sans ça, un canal existant mais resté sans
    # opérateur valide (ex: après un rebuild) restait invisible tant
    # qu'on ne corrigeait pas ça manuellement.
    if not channel.user_ids:
        operator = _get_default_operator(env)
        if operator:
            channel.write({'user_ids': [(4, operator.id)]})
            _logger.info(
                "Opérateur Live Chat assigné automatiquement : %s",
                operator.name,
            )
        else:
            _logger.warning(
                "Aucun utilisateur actif trouvé pour servir d'opérateur "
                "Live Chat — la bulle de chat pourrait ne pas s'afficher. "
                "Assignez un opérateur manuellement via Site Web > "
                "Live Chat."
            )


def post_init_hook(env):
    """Initialise les données Exocoms Group"""

    # === COMPANY ===
    company = _get_company(env)
    if company:
        company.write({
            'name': COMPANY_NAME,
            'email': 'contact@exocoms.fr',
            'phone': '+33 (0)1 84 79 37 55',
            'country_id': env.ref('base.fr').id,
        })

    # === SITE WEB ===
    website = _get_website(env)
    if website:
        website.write({
            'name': WEBSITE_NAME,
            'social_facebook': 'https://www.facebook.com/exocoms',
            'social_twitter': 'https://twitter.com/exocoms',
            'social_linkedin': 'https://www.linkedin.com/company/exocoms',
            'cookies_bar': True,  # Active la bannière RGPD + lien "Politique de cookies" dans le footer
        })

    # === LOGO ===
    _set_logo(env, website)

    # === ASSETS CSS/JS — scopés au site Exocoms uniquement ===
    _setup_theme_assets(env, website)

    # === FOOTER / COPYRIGHT — scopés au site Exocoms uniquement ===
    _scope_layout_views(env, website)

    # === LIVE CHAT — canal dédié Exocoms, scopé nativement via website.channel_id ===
    _setup_livechat(env, website)

    # === LANGUES — Français + Anglais ===
    # NOTE multi-sites : ce bloc ne touche que website.language_ids du
    # SITE Exocoms (website.write), donc déjà scopé correctement.
    lang_fr = env['res.lang'].search([('code', '=', 'fr_FR')], limit=1)
    if not lang_fr:
        env['res.lang']._activate_lang('fr_FR')
        lang_fr = env['res.lang'].search([('code', '=', 'fr_FR')], limit=1)

    lang_en = env['res.lang'].search([('code', '=', 'en_US')], limit=1)

    if website and lang_fr:
        website.write({'language_ids': [(5, 0, 0)]})
        website.write({
            'default_lang_id': lang_fr.id,
            'language_ids': [(4, lang_fr.id)] + ([(4, lang_en.id)] if lang_en else []),
        })

    # === LANGUE PAR DÉFAUT — public_user + website ===
    # ⚠️ ATTENTION CONNUE, NON CORRIGÉE AUTOMATIQUEMENT : base.public_user
    # et base.public_partner sont des enregistrements UNIQUES et GLOBAUX
    # dans Odoo (pas un par site). Sur une base multi-sites, chaque site
    # gère en réalité sa langue via website.default_lang_id (déjà posé
    # ci-dessus) et la détection de langue du navigateur/URL ; modifier
    # la langue du public_user global peut affecter le comportement par
    # défaut perçu sur D'AUTRES sites qui n'auraient pas de
    # default_lang_id explicite. On le garde ici car c'est nécessaire
    # pour Exocoms, mais SI un autre site se met soudain à afficher du
    # français par défaut après cette installation, c'est la cause la
    # plus probable — vérifiez le default_lang_id de chaque site concerné.
    public_user = env.ref('base.public_user', raise_if_not_found=False)
    if public_user and lang_fr:
        public_user.with_context(no_recompute=True).write({'lang': 'fr_FR'})

    public_partner = env.ref('base.public_partner', raise_if_not_found=False)
    if public_partner and lang_fr:
        public_partner.with_context(no_recompute=True).write({'lang': 'fr_FR'})

    # ⚠️ ATTENTION CONNUE, NON CORRIGÉE : ir.config_parameter est GLOBAL
    # à toute la base, pas par site. 'web.base.lang' va changer la langue
    # par défaut du BACKEND Odoo pour tous les utilisateurs de TOUS les
    # projets sur cette base. Sur une base partagée à 17 sites, c'est
    # risqué si d'autres équipes travaillent en anglais sur le backend.
    # Recommandation : commentez ces deux lignes si vous n'êtes pas seul
    # à administrer cette base, ou validez avec les autres responsables.
    params = env['ir.config_parameter'].sudo()
    params.set_param('web.base.lang', 'fr_FR')
    params.set_param('website.default_lang_id', str(lang_fr.id) if lang_fr else 'fr_FR')

    # Charger les traductions françaises officielles Odoo (sans danger,
    # ça ne fait qu'installer des traductions, pas de la config).
    try:
        mods = env['ir.module.module'].search([
            ('name', 'in', [
                'base', 'web', 'website', 'website_sale',
                'portal', 'auth_signup', 'mail', 'sale'
            ]),
            ('state', '=', 'installed')
        ])
        mods._update_translations('fr_FR')
    except Exception:
        pass

    # === MENUS ===
    _setup_menus(env, website, lang_en)

    # === ATTRIBUTS / FILTRES MONÉTIQUE ===
    _setup_monetique_attributes(env, lang_en)

    # === PROFIL DROPDOWN — retrait du doublon "My Account" ===
    _remove_account_dropdown_duplicate(env, website)

    # === DÉCONNEXION — supprimer la vue custom (scopée à notre site) ===
    existing = env['ir.ui.view'].search([
        ('name', '=', 'Exocoms Logout FR'),
        ('website_id', '=', website.id),
    ], limit=1)
    if existing:
        existing.unlink()

    # === DESIGN BOUTIQUE — Chips par défaut (scopé à notre site) ===
    _setup_shop_grid_design(env, website)

    # === PUBLIER NOS PRODUITS — UNIQUEMENT LES NÔTRES, SUR NOTRE SITE ===
    _publish_our_products(env, website, company)

    # === CRÉER TOUTE LA STRUCTURE DE CATÉGORIES ===
    cat = env['product.public.category']

    demo_names = [
        'Desks', 'Furnitures', 'Boxes', 'Drawers',
        'Cabinets', 'Bins', 'Lamps', 'All',
        'Indoor', 'Outdoor', 'Multimedia',
    ]
    # CORRECTIF : on ne supprime ces catégories de démo QUE si elles ne
    # sont rattachées à aucun site (vraies données de démo Odoo) ou
    # spécifiquement à notre site. On ne touche jamais aux catégories
    # de démo qu'un AUTRE site aurait gardées intentionnellement.
    cats_demo = cat.search([
        ('name', 'in', demo_names),
        ('website_id', 'in', [False, website.id]),
    ])
    if cats_demo:
        cats_demo.unlink()

    def _find_by_name_ci(records, target_name):
        """Recherche insensible à la CASSE UNIQUEMENT (pas aux accents),
        faite en Python plutôt qu'en SQL (cf. souci de locale PostgreSQL
        avec '=ilike' qui peut aussi ignorer les accents)."""
        target = target_name.strip().lower()
        return next((r for r in records if r.name and r.name.strip().lower() == target), None)

    def get_or_create(name, parent=None, seq=10):
        # CORRECTIF MAJEUR : sur une base à 17 sites, des catégories
        # génériques ("Services", "Accessoires", "Crypto"...) existent
        # très probablement déjà pour d'autres projets, avec ou sans
        # website_id. On ne réutilise désormais QUE :
        #   (a) une catégorie déjà explicitement à NOUS (website_id =
        #       website.id), ou
        #   (b) à défaut, on en CRÉE une nouvelle pour nous — on ne vole
        #       JAMAIS la catégorie d'un autre site, même orpheline,
        #       même si le nom correspond exactement.
        siblings = cat.search([
            ('parent_id', '=', parent.id if parent else False),
            ('website_id', '=', website.id),
        ])
        c = _find_by_name_ci(siblings, name)
        if not c:
            vals = {
                'name': name,
                'sequence': seq,
                'website_id': website.id,
            }
            if parent:
                vals['parent_id'] = parent.id
            c = cat.create(vals)
            _logger.info("Catégorie CRÉÉE : '%s' (parent: %s)", name, parent.name if parent else '-')
        else:
            _logger.info("Catégorie RETROUVÉE : '%s' -> id=%s (déjà existante, site Exocoms)", name, c.id)
            _logger.info("Catégorie RETROUVÉE : '%s' -> id=%s (déjà existante, site Exocoms)", name, c.id)
        return c

    informatique = get_or_create('Informatique & Réseaux', seq=1)
    monetique_root = get_or_create('Monétique', seq=2)
    telecom = get_or_create('Télécom', seq=3)

    # CORRECTIF : la recherche "Monetique" sans accent au niveau racine
    # est désormais aussi scopée à notre site, pour ne pas réorganiser
    # une catégorie appartenant à un autre projet.
    monetique_sub = _find_by_name_ci(
        cat.search([('parent_id', '=', False), ('website_id', '=', website.id)]),
        'Monetique'
    )
    if monetique_sub and monetique_sub.id != monetique_root.id:
        monetique_sub.write({
            'parent_id': monetique_root.id,
            'sequence': 1,
        })

    pdv = cat.search([
        ('name', 'ilike', 'Point de vente'),
        ('parent_id', '=', False),
        ('website_id', '=', website.id),
    ], limit=1)
    if pdv:
        pdv.write({
            'parent_id': monetique_root.id,
            'sequence': 2,
        })

    # Réattacher "Crypto"/"CRYPTO" existant (racine préexistante sur ce
    # site) sous Monétique — par nom, jamais par ID. Les produits déjà
    # liés le restent automatiquement (on ne fait que déplacer le
    # parent), aucune migration nécessaire ici.
    crypto_root = cat.search([
        ('name', 'ilike', 'Crypto'),
        ('parent_id', '=', False),
        ('website_id', '=', website.id),
    ], limit=1)
    if crypto_root:
        crypto_root.write({
            'parent_id': monetique_root.id,
            'sequence': 6,
        })

    # Réattacher "Distributeur automatique" existant (racine) sous
    # Monétique — même logique, aucune perte de données.
    distrib_root = cat.search([
        ('name', 'ilike', 'Distributeur automatique'),
        ('parent_id', '=', False),
        ('website_id', '=', website.id),
    ], limit=1)
    if distrib_root:
        distrib_root.write({
            'parent_id': monetique_root.id,
            'sequence': 4,
        })

    # RÉCUPÉRATION complète de l'ancienne catégorie racine
    # "Informatique" (nom différent du nôtre, donc impossible à
    # réattacher par simple déplacement de parent comme ci-dessus) :
    # migre tous ses produits vers "Informatique & Réseaux", puis
    # archive l'ancienne (jamais supprimée).
    _merge_root_category(env, website, 'Informatique', informatique)

    get_or_create('Matériel & Informatique Générale', informatique, seq=1)
    get_or_create('Réseaux & Infrastructure', informatique, seq=2)
    get_or_create('Communication & Vidéo', informatique, seq=3)
    info_logiciels = get_or_create('Logiciels', informatique, seq=4)
    get_or_create('Cybersécurité', info_logiciels)

    monetique = _find_by_name_ci(
        cat.search([('parent_id', '=', monetique_root.id), ('website_id', '=', website.id)]),
        'Monetique'
    )
    if not monetique:
        monetique = cat.create({
            'name': 'Monetique',
            'parent_id': monetique_root.id,
            'sequence': 1,
            'website_id': website.id,
        })
        _logger.info("Catégorie CRÉÉE : 'Monetique' (sous-catégorie de Monétique)")
    else:
        _logger.info("Catégorie RETROUVÉE : 'Monetique' -> id=%s (déjà existante)", monetique.id)

    caisse = get_or_create('Caisse Enregistreuse', monetique_root, seq=3)
    get_or_create('Distributeur automatique', monetique_root, seq=4)
    monnaie = get_or_create('Monnaie & Chèque', monetique_root, seq=5)
    crypto = get_or_create('Crypto', monetique_root, seq=6)
    accessoires = get_or_create('Accessoires', monetique_root, seq=7)
    consommables = get_or_create('Consommables', monetique_root, seq=8)
    services = get_or_create('Services', monetique_root, seq=9)

    # --- TPE : casse des marques normalisée (Ingenico, Pax, Verifone,
    # Urovo, Sunmi, Castles — première lettre majuscule uniquement) ---
    tpe_fixe = get_or_create('TPE Fixe', monetique, seq=1)
    get_or_create('Ingenico', tpe_fixe)
    get_or_create('Pax', tpe_fixe)
    get_or_create('Verifone', tpe_fixe)

    tpe_portable = get_or_create('TPE Portable', monetique, seq=2)
    get_or_create('Ingenico', tpe_portable)
    get_or_create('Pax', tpe_portable)
    get_or_create('Urovo', tpe_portable)
    get_or_create('Sunmi', tpe_portable)

    tpe_mobile = get_or_create('TPE Mobile', monetique, seq=3)
    get_or_create('Ingenico', tpe_mobile)
    get_or_create('Pax', tpe_mobile)
    get_or_create('Urovo', tpe_mobile)
    get_or_create('Sunmi', tpe_mobile)
    get_or_create('Verifone', tpe_mobile)
    get_or_create('Castles', tpe_mobile)

    tpe_sante = get_or_create('TPE Santé', monetique, seq=4)
    get_or_create('Ingenico', tpe_sante)
    get_or_create('Pax', tpe_sante)

    pin_pad = get_or_create('PIN Pad', monetique, seq=5)
    get_or_create('Ingenico', pin_pad)
    get_or_create('Pax', pin_pad)

    logiciels_tpe = get_or_create('Logiciels TPE', monetique, seq=6)
    get_or_create('Ingenico', logiciels_tpe)
    get_or_create('Verifone', logiciels_tpe)
    get_or_create('Pax', logiciels_tpe)
    get_or_create('Logiciels pour Pax', logiciels_tpe)

    passerelles = get_or_create('Passerelles', monetique, seq=7)
    get_or_create('Passerelle IP', passerelles)
    get_or_create('Passerelle 3G/4G', passerelles)

    # --- Caisse Enregistreuse : Logiciels/Consommables/Services ne
    # sont PLUS créées ici (Cybersécurité -> Informatique & Réseaux,
    # HP -> Consommables racine, produits Services -> Services >
    # Caisse Enregistreuse) — on ne recrée pas de conteneurs vides. ---
    caisse_tactile = get_or_create('Caisse Tactile', caisse, seq=1)
    sunmi_cat = get_or_create('Sunmi', caisse_tactile)
    get_or_create('Sunmi D3 80mm', sunmi_cat)
    get_or_create('Sunmi D3 PRO', sunmi_cat)
    get_or_create('Sunmi D3 MINI', sunmi_cat)
    get_or_create('Sunmi T3', sunmi_cat)
    get_or_create('Pax', caisse_tactile)

    imprimante = get_or_create('Imprimante', caisse, seq=2)
    get_or_create('Imprimante Ticket', imprimante)
    get_or_create('Imprimante Etiquette', imprimante)

    get_or_create('Kiosques', caisse, seq=3)
    get_or_create('Accessoires', caisse, seq=5)
    get_or_create('Écrans tactiles / moniteurs', caisse, seq=8)
    get_or_create('Tiroirs caisses', caisse, seq=9)
    get_or_create('Afficheurs', caisse, seq=10)

    get_or_create('Scanner de Chèque', monnaie)
    get_or_create('Lecteur de Chèque', monnaie)
    detecteurs = get_or_create('Détecteurs et Compteuses', monnaie)
    get_or_create('Compteuse de Pièces', detecteurs)
    get_or_create('Compteuse de Billets', detecteurs)
    get_or_create('Détecteurs', detecteurs)
    get_or_create('Accessoires', monnaie)

    get_or_create('ATM', crypto)
    get_or_create('Logiciel ATM', crypto)
    get_or_create('Formation ATM', crypto)

    get_or_create('Batteries TPE', accessoires)
    chargeurs = get_or_create('Chargeurs & Alimentations', accessoires)
    get_or_create('Ingenico', chargeurs)
    get_or_create('Pax', chargeurs)
    cables = get_or_create('Cables', accessoires)
    get_or_create('Ingenico', cables)
    get_or_create('Verifone', cables)
    get_or_create('Housses & protections', accessoires)
    # 'Pièces détachées' n'est plus créée ici : ses produits ont été
    # déplacés vers Monétique > Services > Pièces Détachées.

    get_or_create('Monetique', consommables)
    get_or_create('Pitney Bowes', consommables)
    get_or_create('Panini', consommables)
    get_or_create("DOC'UP", consommables)
    get_or_create('HP', consommables)
    get_or_create('Autres', consommables)

    get_or_create('Monetique', services)
    get_or_create('Caisse Enregistreuse', services)
    get_or_create('Pièces Détachées', services)
    get_or_create('Assistance', services)

    equip = get_or_create('Équipements Électriques', telecom)
    get_or_create('Onduleurs & électricité', equip)
    get_or_create('Câbles', equip)
    get_or_create('Accessoires', equip)

    solutions_pro = get_or_create('Solutions Professionnelles Spécifiques', telecom)
    get_or_create('Points de ventes', solutions_pro)
    get_or_create('Domotique', solutions_pro)
    get_or_create('PLV / Marketing', solutions_pro)

    solutions_tel = get_or_create('Solutions Télécom', telecom)
    get_or_create("Centre d'appel", solutions_tel)
    get_or_create('Visioconférence', solutions_tel)
    get_or_create('Collaboration', solutions_tel)
    get_or_create('Communication unifiée', solutions_tel)

    # Publier tous les produits existants sous nos 3 catégories
    # racines (et leurs sous-catégories) — corrige le cas où une
    # catégorie récupérée (Crypto, Distributeur automatique,
    # Informatique...) est bien publiée, mais où ses PRODUITS restent
    # marqués 'Non publié' (champ indépendant de la catégorie).
    for root in (informatique, monetique_root, telecom):
        _publish_category_tree_products(env, website, root)

    # NOTE : Le footer et le copyright sont gérés par
    # views/templates/footer.xml (templates custom_footer et
    # custom_copyright, inherit_id="website.layout"). Ils sont
    # désormais scopés au site Exocoms via _scope_layout_views(),
    # appelée juste après _setup_theme_assets() ci-dessus.


def post_migrate_hook(env):
    """S'exécute à chaque update du module — strictement scopé à notre site."""
    website = _get_website(env)
    company = _get_company(env)
    lang_en = env['res.lang'].search([('code', '=', 'en_US')], limit=1)

    # Logo maintenu à chaque update (au cas où le site ait été recréé)
    _set_logo(env, website)

    # Assets CSS/JS maintenus, scopés au site Exocoms
    _setup_theme_assets(env, website)

    # Footer/copyright maintenus, scopés au site Exocoms
    _scope_layout_views(env, website)

    # Live Chat maintenu, scopé au site Exocoms
    _setup_livechat(env, website)

    # Menus maintenus + nettoyage démo à chaque update
    _setup_menus(env, website, lang_en)

    # Attributs/filtres maintenus + traduction à chaque update
    _setup_monetique_attributes(env, lang_en)

    if website:
        # CORRECTIF MAJEUR : la version originale rattachait À CHAQUE
        # UPDATE tout produit/catégorie orphelin (sans website_id) de
        # TOUTE LA BASE au site Exocoms. Sur une base à 17 sites, c'est
        # la cause la plus probable de "mon module s'affiche aussi sur
        # les autres sites" si ce hook tourne après qu'un autre projet
        # ait laissé des produits/catégories temporairement orphelins
        # (en cours de configuration, par exemple). On utilise désormais
        # la même fonction strictement scopée que dans post_init_hook.
        _publish_our_products(env, website, company)

        # Pour les catégories : on ne rattache plus aveuglément les
        # orphelines. Le système get_or_create (dans post_init_hook) les
        # crée déjà avec website_id posé dès le départ ; il n'y a donc
        # normalement plus besoin de rattachement de masse ici. Si vous
        # constatez des catégories Exocoms orphelines malgré tout,
        # préférez un script de diagnostic ciblé (liste des noms exacts
        # attendus) plutôt qu'un rattachement de masse aveugle.

        try:
            website.write({
                'shop_opt_products_design_classes': (
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
                ),
            })
        except Exception:
            _logger.exception("Échec écriture shop_opt_products_design_classes")

        # Vues qweb (grid produits) maintenues à chaque update, scopées.
        _setup_shop_grid_design(env, website)
        _remove_account_dropdown_duplicate(env, website)