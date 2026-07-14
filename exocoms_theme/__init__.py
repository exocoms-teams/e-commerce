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
    'exocoms_theme/static/src/css/avis_hero.css',
    'exocoms_theme/static/src/css/avis_content.css',
    'exocoms_theme/static/src/css/avis_hero.css',
    'exocoms_theme/static/src/css/avis_content.css',
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
            # CORRECTIF MAJEUR : un attribut du MÊME NOM peut déjà exister
            # en base partagée (17 sites), créé par un autre projet avec le
            # mode par défaut Odoo 'create_variant=always'. Sans cette
            # correction, on rattachait ensuite cet attribut existant (mode
            # 'always') à des dizaines de produits avec toutes ses valeurs
            # -> explosion combinatoire de variantes et erreur "nombre de
            # variantes supérieur à la limite autorisée". On force donc
            # TOUJOURS 'no_variant', qu'il ait été créé par nous ou non.
            if attr.create_variant != 'no_variant':
                try:
                    attr.write({'create_variant': 'no_variant'})
                except Exception:
                    # Filet de sécurité : si CET attribut sert déjà à
                    # générer de vraies variantes sur un produit existant,
                    # Odoo refuse le changement de mode (à raison — ça
                    # casserait ce produit). On logue clairement plutôt
                    # que de faire planter toute la mise à jour du module :
                    # dans ce cas, il faut choisir un nom d'attribut
                    # distinct dans attr_names ci-dessous et dans
                    # _attach_monetique_attributes_to_products(), comme ça
                    # a été fait pour 'Forfait DATA par TPE' -> 'Forfait
                    # DATA compatible'.
                    _logger.exception(
                        "Impossible de forcer create_variant='no_variant' "
                        "sur l'attribut '%s' (id=%s) — probablement déjà "
                        "utilisé pour générer de vraies variantes sur un "
                        "produit existant. Utilisez un nom distinct pour "
                        "l'attribut de filtre boutique.",
                        name_fr, attr.id,
                    )

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

    # CORRECTIF MAJEUR : renommé depuis 'Forfait DATA par TPE' -> ce nom
    # exact est déjà utilisé, configuré MANUELLEMENT en backend, sur le
    # produit "Connexions monétiques 4G/5G..." pour générer ses 3 VRAIES
    # variantes de prix (5 Mo/50 Mo/100 Mo) — un attribut en mode
    # 'Chaque combinaison', légitime pour CE produit précis. Notre usage
    # ici est différent : un simple filtre boutique (mode 'no_variant')
    # à rattacher à TOUS les produits Monétique (TPE, etc.). Réutiliser
    # le même nom réutilisait le MÊME attribut, provoquant soit une
    # explosion de variantes (si on force son mode), soit un refus
    # d'Odoo ("vous ne pouvez pas modifier le mode... utilisé sur...").
    # D'où ce nom distinct, qui ne rentre plus jamais en collision.
    forfait = get_or_create_attribute(
        'Forfait DATA compatible', 'Compatible Data Plan',
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


def _attach_monetique_attributes_to_products(env, website):
    """CORRECTIF : _setup_monetique_attributes() ci-dessus crée bien les
    attributs/valeurs (Forfait DATA, Chèques, Garantie, Type de modèle,
    Quantité), mais uniquement comme catalogue GLOBAL
    (product.attribute / product.attribute.value) — ils n'étaient
    jamais rattachés à un produit réel. Or Odoo n'affiche un filtre
    boutique QUE pour les attributs effectivement portés par au moins
    un produit du résultat affiché (product.template.attribute_line_ids).
    Sans ce rattachement, les filtres restent invisibles dans la
    sidebar boutique même si les attributs existent bien en base —
    c'est exactement ce qui se passait ici.

    CORRECTIF (pertinence) : chaque attribut n'est plus rattaché à TOUS
    les produits Monétique en bloc, mais uniquement à la sous-catégorie
    où il a du sens (ex: 'Nombre de chèques par mois' seulement sur les
    scanners/lecteurs de chèques, pas sur un TPE) — voir ATTR_SCOPE dans
    le corps de la fonction. Seul 'Garantie' reste large. Comme ces
    attributs sont en create_variant='no_variant' (voir ci-dessus), ce
    rattachement ne crée AUCUNE variante supplémentaire ni de doublon de
    produit — il rend juste l'attribut visible/filtrable côté boutique.
    Idempotent : un produit qui a déjà une ligne pour un attribut donné
    n'est pas retouché (pour ne pas écraser une sélection de valeurs
    déjà affinée manuellement en backend).
    """
    if not website:
        _logger.warning(
            "_attach_monetique_attributes_to_products : aucun site fourni, "
            "abandon immédiat."
        )
        return

    Category = env['product.public.category']
    monetique_root = Category.search([
        ('name', '=', 'Monétique'), ('parent_id', '=', False), ('website_id', '=', website.id),
    ], limit=1)
    if not monetique_root:
        _logger.warning(
            "_attach_monetique_attributes_to_products : aucune catégorie "
            "racine 'Monétique' trouvée pour le site %s (id=%s) — "
            "rattachement abandonné. Vérifiez le nom exact (accent) et le "
            "website_id de la catégorie en base.",
            website.name, website.id,
        )
        return

    def _find_child(name, parent_id):
        return Category.search([
            ('name', '=', name), ('parent_id', '=', parent_id), ('website_id', '=', website.id),
        ], limit=1)

    def _tree_products(root_cat):
        tree = root_cat | Category.search([('id', 'child_of', root_cat.ids)])
        return env['product.template'].search([
            ('public_categ_ids', 'in', tree.ids),
            ('website_id', '=', website.id),
        ])

    all_products = _tree_products(monetique_root)
    if not all_products:
        _logger.warning(
            "_attach_monetique_attributes_to_products : catégorie 'Monétique' "
            "trouvée (id=%s) mais AUCUN produit scopé au site %s (id=%s) "
            "n'y est rattaché — rattachement abandonné. Vérifiez que les "
            "produits Monétique ont bien website_id=%s.",
            monetique_root.id, website.name, website.id, website.id,
        )
        return

    # CORRECTIF (pertinence des filtres) : rattacher les 5 attributs à
    # TOUS les produits Monétique en bloc faisait apparaître des filtres
    # hors-sujet (ex: "Nombre de chèques par mois" sur un TPE). Chaque
    # attribut n'est donc désormais rattaché qu'aux produits de la
    # sous-catégorie où il a vraiment du sens. 'Garantie' reste large
    # (pertinent pour tout matériel durable). 'None' = toute la gamme
    # Monétique. Repose sur la structure de catégories construite par
    # get_or_create() plus haut dans ce hook (noms/parents identiques).
    monetique_sub = _find_child('Monetique', monetique_root.id)  # sous-branche TPE
    monnaie = _find_child('Monnaie & Chèque', monetique_root.id)
    consommables = _find_child('Consommables', monetique_root.id)
    accessoires = _find_child('Accessoires', monetique_root.id)
    cables = _find_child('Cables', accessoires.id) if accessoires else None

    ATTR_SCOPE = {
        'Garantie': None,
        'Forfait DATA compatible': monetique_sub,
        'Nombre de chèques par mois': monnaie,
        'Type de modèle': cables,
        'Quantité': consommables,
    }

    # CORRECTIF MAJEUR : _setup_monetique_attributes() crée ces attributs
    # avec .with_context(lang='fr_FR') -- leur nom est donc stocké dans
    # la traduction française. Rechercher par 'name' SANS ce même contexte
    # de langue ne matche pas forcément la bonne traduction sur un champ
    # traduisible, et retournait 0 résultat en conditions réelles (voir
    # logs : "AUCUN attribut trouvé" alors qu'ils existent bien en base).
    attr_names = list(ATTR_SCOPE.keys())
    attrs = env['product.attribute'].with_context(lang='fr_FR').search([('name', 'in', attr_names)])
    if not attrs:
        _logger.warning(
            "_attach_monetique_attributes_to_products : AUCUN attribut "
            "trouvé parmi %s — _setup_monetique_attributes() a-t-elle bien "
            "été appelée avant celle-ci ? Rattachement abandonné.",
            attr_names,
        )
        return
    if len(attrs) < len(attr_names):
        found_names = set(attrs.mapped('name'))
        _logger.warning(
            "_attach_monetique_attributes_to_products : seulement %s/%s "
            "attributs trouvés (manquants : %s) — noms probablement "
            "différents en base (accents/casse).",
            len(attrs), len(attr_names),
            [n for n in attr_names if n not in found_names],
        )

    # Filet de sécurité : ne JAMAIS rattacher un attribut resté en mode
    # 'always'/'dynamic' (variante réelle) — même si get_or_create_attribute()
    # n'a pas réussi à le forcer en 'no_variant' (cf. son propre filet de
    # sécurité). L'attacher tel quel à des dizaines de produits provoquerait
    # l'erreur "nombre de variantes supérieur à la limite autorisée".
    unsafe_attrs = attrs.filtered(lambda a: a.create_variant != 'no_variant')
    if unsafe_attrs:
        _logger.warning(
            "_attach_monetique_attributes_to_products : %s attribut(s) "
            "ignoré(s) car pas en mode 'no_variant' (%s) — probablement "
            "déjà utilisé pour de vraies variantes ailleurs. Choisissez un "
            "nom distinct dans _setup_monetique_attributes().",
            len(unsafe_attrs), unsafe_attrs.mapped('name'),
        )
        attrs = attrs - unsafe_attrs
    if not attrs:
        return

    _logger.info(
        "_attach_monetique_attributes_to_products : %s produit(s) trouve(s) "
        "sous la categorie Monetique (id=%s) pour le site %s, %s "
        "attribut(s) cible(s) trouve(s) en base.",
        len(all_products), monetique_root.id, website.name, len(attrs),
    )

    total_attached = 0
    for attr in attrs:
        scope_cat = ATTR_SCOPE.get(attr.name)
        if scope_cat is None:
            products = all_products
            scope_label = 'toute la gamme Monétique'
        elif not scope_cat:
            _logger.warning(
                "_attach_monetique_attributes_to_products : sous-catégorie "
                "cible introuvable pour l'attribut '%s' — ignoré (vérifiez "
                "que l'arborescence de catégories a bien été construite "
                "avant cet appel).",
                attr.name,
            )
            continue
        else:
            products = _tree_products(scope_cat)
            scope_label = "sous-catégorie '%s' (id=%s)" % (scope_cat.name, scope_cat.id)

        if not products or not attr.value_ids:
            continue

        attached = 0
        for product in products:
            existing_attr_ids = set(product.attribute_line_ids.mapped('attribute_id').ids)
            if attr.id in existing_attr_ids:
                continue
            product.write({'attribute_line_ids': [
                (0, 0, {'attribute_id': attr.id, 'value_ids': [(6, 0, attr.value_ids.ids)]}),
            ]})
            attached += 1

        total_attached += attached
        _logger.info(
            "Attribut '%s' rattaché à %s produit(s) (portée : %s).",
            attr.name, attached, scope_label,
        )

    if total_attached:
        _logger.info(
            "Attributs Monétique rattachés à %s produit(s) au total — "
            "filtres boutique désormais visibles, chacun sur sa sous-"
            "catégorie pertinente.",
            total_attached,
        )
    else:
        _logger.info(
            "_attach_monetique_attributes_to_products : 0 produit modifié -- "
            "ils ont déjà tous les attributs pertinents (rien à faire), "
            "normal si la fonction a déjà tourné avec succès."
        )


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
    """CORRECTIF DE SÉCURITÉ (incident constaté) : cette fonction
    publiait auparavant tout produit orphelin (website_id=False) SANS
    société assignée (company_id=False inclus dans le domaine) — bien
    trop permissif sur une base partagée à 17 sites. Résultat observé
    en conditions réelles : 25 produits d'AUTRES projets (plomberie,
    matériel réseau Cisco, hôtellerie, frais de réservation...) se
    sont retrouvés publiés par erreur sur le site Exocoms après un
    rebuild, simplement parce qu'ils n'avaient ni site ni société.

    Cette fonction ne fait plus AUCUNE supposition sur des produits
    orphelins génériques. Elle ne publie que des produits dont la
    société correspond STRICTEMENT à la nôtre — jamais de fallback
    sur company_id=False.
    """
    try:
        if not company:
            return
        domain = [
            ('is_published', '=', False),
            ('website_id', '=', False),
            ('company_id', '=', company.id),  # correspondance stricte, jamais de fallback False
        ]
        products = env['product.template'].search(domain)
        if products:
            products.write({
                'is_published': True,
                'website_id': website.id,
            })
    except Exception:
        _logger.exception("Échec publication des produits Exocoms")


LEGACY_SITE_NAME = 'EXOCOMS'  # nom exact (tout en majuscules) du site préexistant, source réelle de nos produits


def _migrate_products_from_legacy_site(env, website):
    """Migre vers NOTRE site les produits déjà PUBLIÉS sur le site
    préexistant 'EXOCOMS' (celui qui existait avant ce module, dans
    la base partagée à 17 sites) — jamais de produits orphelins
    génériques, uniquement ceux confirmés comme appartenant à ce site
    précis, par son ID exact (jamais deviné).

    Remplace l'ancienne logique d'adoption d'orphelins, responsable
    d'un incident de sécurité (cf. _publish_our_products ci-dessus).
    Idempotente : sans effet si déjà migré (les produits ont alors
    website_id = le nôtre, donc exclus du domaine de recherche).

    CORRECTIF 1 : exclut explicitement les produits GÉNÉRIQUES natifs
    d'Odoo (carte-cadeau, acompte, frais de réservation...) qui sont
    souvent publiés sur N'IMPORTE QUEL site par défaut — confirmé en
    conditions réelles : ils s'étaient invités dans notre catalogue.

    CORRECTIF 2 : la redistribution fine par mot-clé (Portable/Mobile/
    Santé/PIN Pad/Logiciel) est désormais AUTOMATISÉE ici — auparavant
    seulement documentée en commentaire, elle devait être relancée à
    la main à chaque migration, ce qui a été oublié au moins deux fois
    en conditions réelles (produits Ingenico/Pax tous entassés sous
    'TPE Fixe' au lieu de Portable/Mobile/Santé/PIN Pad/Logiciels TPE).

    Les catégories sont réassignées par correspondance de NOM avec
    notre propre arborescence (déjà construite à ce stade du hook).
    """
    if not website:
        return
    legacy = env['website'].search([
        ('name', '=', LEGACY_SITE_NAME),
        ('id', '!=', website.id),
    ], limit=1)
    if not legacy:
        return

    Product = env['product.template']
    Category = env['product.public.category']

    # Produits génériques natifs d'Odoo à ne jamais migrer (frais de
    # réservation, carte-cadeau, e-wallet, acomptes...) — non
    # spécifiques à Exocoms, publiés par défaut sur de nombreux sites.
    GENERIC_PRODUCT_NAMES = [
        'Frais de réservation', 'Booking Fees',
        'Carte-cadeau', 'Gift Card',
        'Recharger le e-wallet', 'Top-up eWallet',
        'Deposit', 'Down Payment (POS)', 'Down Payment',
        'Déplacement',
    ]

    legacy_products = Product.search([
        ('website_id', '=', legacy.id),
        ('is_published', '=', True),
        ('name', 'not in', GENERIC_PRODUCT_NAMES),
    ])
    if not legacy_products:
        return

    legacy_categories = Category.search([('website_id', '=', legacy.id)])
    our_categories = Category.search([('website_id', '=', website.id)])
    our_by_name = {}
    for c in our_categories:
        our_by_name.setdefault(c.name.strip().lower(), []).append(c)

    # CORRECTIF (produits perdus) : deux noms peuvent désigner la même
    # chose avec une orthographe légèrement différente entre l'ancien
    # site et notre arborescence (ex: 'Housses et protections' vs
    # 'Housses & protections') -- une comparaison stricte ne matchait
    # pas, et le code retirait ALORS la catégorie du produit SANS rien
    # remettre à la place : le produit se retrouvait sans catégorie du
    # tout, invisible dans le filtre boutique correspondant (constaté en
    # conditions réelles sur 'Accessoires'). On normalise donc d'abord
    # les variantes de connecteurs (' et ' <-> ' & ') avant de comparer.
    def _normalize(name):
        n = name.strip().lower()
        return n.replace(' et ', ' & ').replace(' & ', ' et ')

    our_by_name_alt = {}
    for c in our_categories:
        our_by_name_alt.setdefault(_normalize(c.name), []).append(c)

    # CORRECTIF (autres noms divergents constatés) : certains noms de
    # catégorie de l'ancien site n'ont RIEN de commun textuellement avec
    # le nôtre (pas juste 'et'/'&') -- ex: 'Bases chargeur' (legacy) vs
    # 'Chargeurs & Alimentations' (nous). Une normalisation de symboles
    # ne peut pas deviner ça : on maintient donc une liste explicite
    # d'alias, à compléter au fur et à mesure qu'on en découvre
    # (comparer visuellement le site EXOCOMS legacy à notre boutique
    # reste le meilleur moyen de les repérer).
    CATEGORY_NAME_ALIASES = {
        'bases chargeur': 'chargeurs & alimentations',
    }

    # CORRECTIF (collision de noms) : certains noms existent à PLUSIEURS
    # endroits de notre arborescence (ex: 'Caisse Enregistreuse' existe
    # à la fois comme grosse catégorie principale ET comme sous-
    # catégorie de 'Services') -- déjà documenté dans le PDF de
    # réorganisation ('Ingenico' existe sous 8 branches différentes).
    # Prendre candidates[0] au hasard pouvait donc envoyer un produit
    # dans la MAUVAISE branche, tout en laissant la bonne vide. On
    # départage désormais par le nom du PARENT côté legacy quand
    # plusieurs candidats existent.
    def _match_category(name, legacy_parent_name=None):
        key = name.strip().lower()
        candidates = (
            our_by_name.get(key)
            or our_by_name_alt.get(_normalize(name))
            or our_by_name.get(CATEGORY_NAME_ALIASES.get(key, ''))
        )
        if not candidates:
            return None
        if len(candidates) > 1 and legacy_parent_name:
            parent_key = legacy_parent_name.strip().lower()
            for c in candidates:
                if c.parent_id and c.parent_id.name.strip().lower() == parent_key:
                    return c
        return candidates[0]

    legacy_products.write({'website_id': website.id, 'is_published': True})

    remapped = 0
    fallback_used = 0
    unmatched_names = set()
    for p in legacy_products:
        old_categs = p.public_categ_ids.filtered(lambda c: c.id in legacy_categories.ids)
        if not old_categs:
            continue
        new_categs = Category
        for oc in old_categs:
            match = _match_category(oc.name, oc.parent_id.name if oc.parent_id else None)
            if match:
                new_categs |= match
                continue
            # CORRECTIF (repli) : toujours essayer les catégories
            # ANCÊTRES de oc (dans l'arbre du site legacy) avant
            # d'abandonner -- mieux vaut rattacher le produit à un
            # parent large et pertinent (ex: 'Accessoires') que de le
            # laisser totalement orphelin de catégorie.
            ancestor = oc.parent_id
            fallback_match = None
            while ancestor:
                grandparent_name = ancestor.parent_id.name if ancestor.parent_id else None
                fallback_match = _match_category(ancestor.name, grandparent_name)
                if fallback_match:
                    break
                ancestor = ancestor.parent_id
            if fallback_match:
                new_categs |= fallback_match
                fallback_used += 1
            else:
                unmatched_names.add(oc.name)
        kept = p.public_categ_ids - old_categs
        p.write({'public_categ_ids': [(6, 0, (new_categs | kept).ids)]})
        remapped += 1

    _logger.info(
        "%s produit(s) migré(s) depuis le site préexistant '%s' vers %s "
        "(%s recatégorisé(s), %s replié(s) sur une catégorie parente).",
        len(legacy_products), LEGACY_SITE_NAME, website.name, remapped, fallback_used,
    )
    if unmatched_names:
        _logger.warning(
            "Noms de catégorie sans AUCUN équivalent (ni direct ni via un "
            "parent) lors de la migration depuis '%s' : %s. Ajoutez-les "
            "dans get_or_create() si nécessaire, puis relancez -u.",
            LEGACY_SITE_NAME, sorted(unmatched_names),
        )

    # CORRECTIF (audit) : filet de sécurité final -- liste explicitement,
    # produit par produit, tout ce qui s'est quand même retrouvé sans
    # AUCUNE catégorie après migration (cas résiduel : produit dont la
    # seule catégorie legacy n'a ni correspondance directe ni ancêtre
    # matché). Sans ce log, ce genre de trou n'est visible qu'en cliquant
    # manuellement site par site, comme ce qui vient de se passer.
    orphaned = legacy_products.filtered(lambda p: not p.public_categ_ids)
    if orphaned:
        _logger.warning(
            "%s produit(s) migré(s) SANS AUCUNE catégorie après "
            "migration -- invisibles dans tous les filtres boutique : %s",
            len(orphaned), orphaned.mapped('name'),
        )

    # --- Redistribution fine automatique par mot-clé ---
    # Les produits Ingenico/Pax se retrouvent tous sous "TPE Fixe" par
    # la correspondance de nom simple ci-dessus (une seule catégorie
    # "Ingenico"/"Pax" existe par marque au moment du premier mapping
    # trouvé). On les redistribue ici vers leur vraie sous-catégorie,
    # déduite du nom du produit lui-même.
    def _get_or_none(name, parent_id):
        return Category.search([
            ('name', '=', name), ('parent_id', '=', parent_id), ('website_id', '=', website.id),
        ], limit=1)

    monetique_root = Category.search([
        ('name', '=', 'Monétique'), ('parent_id', '=', False), ('website_id', '=', website.id),
    ], limit=1)
    monetique_sub = _get_or_none('Monetique', monetique_root.id) if monetique_root else None
    tpe_fixe = _get_or_none('TPE Fixe', monetique_sub.id) if monetique_sub else None

    if tpe_fixe:
        keyword_targets = [
            ('Portable', 'TPE Portable'), ('Mobile', 'TPE Mobile'), ('Santé', 'TPE Santé'),
            ('Pinpad', 'PIN Pad'), ('PIN Pad', 'PIN Pad'), ('Logiciel', 'Logiciels TPE'),
        ]
        redistributed = 0
        for brand in ['Ingenico', 'Pax']:
            brand_cat = _get_or_none(brand, tpe_fixe.id)
            if not brand_cat:
                continue
            brand_products = Product.search([
                ('public_categ_ids', 'in', brand_cat.id), ('website_id', '=', website.id),
            ])
            for p in brand_products:
                matched = None
                for kw, target_name in keyword_targets:
                    if kw in p.name:
                        matched = target_name
                        break
                if matched:
                    target_parent = _get_or_none(matched, monetique_sub.id)
                    target_cat = _get_or_none(brand, target_parent.id) if target_parent else None
                    if target_cat and target_cat.id != brand_cat.id:
                        new_categs = (p.public_categ_ids - brand_cat) | target_cat
                        p.write({'public_categ_ids': [(6, 0, new_categs.ids)]})
                        redistributed += 1
        if redistributed:
            _logger.info(
                "%s produit(s) redistribué(s) automatiquement depuis 'TPE Fixe' "
                "vers leur vraie sous-catégorie (Portable/Mobile/Santé/PIN Pad/Logiciel).",
                redistributed,
            )


def _repair_orphaned_categories(env, website):
    """FILET DE RATTRAPAGE pour des produits déjà passés sur notre site
    (website_id posé) mais restés SANS AUCUNE catégorie — séquelle du
    bug de correspondance de noms dans _migrate_products_from_legacy_site()
    (ex: 'Housses et protections' vs 'Housses & protections' : aucun
    match, l'ancienne catégorie était retirée SANS rien remettre à la
    place) survenue lors d'une migration effectuée AVANT ce correctif.

    Pourquoi une fonction séparée : une fois qu'un produit a quitté le
    site legacy (website_id changé vers le nôtre), le domaine de
    recherche de _migrate_products_from_legacy_site() ('website_id' =
    legacy) ne le revoit plus JAMAIS lors d'un rejeu — rejouer cette
    fonction ne suffit donc pas à réparer les dégâts déjà faits. Ce
    filet cherche directement, côté NOTRE site, tout produit publié
    sans aucune catégorie, et tente de le rattacher automatiquement par
    mot-clé trouvé dans son nom (ex: 'Coque de protection...' contient
    'Housses & protections'? non — voir la liste de nos catégories
    feuilles ci-dessous, comparaison insensible à la casse).

    Idempotent : ne retouche jamais un produit qui a déjà au moins une
    catégorie. Volontairement PRUDENT : si aucun mot-clé ne matche, le
    produit est juste signalé dans les logs pour une catégorisation
    manuelle — jamais de repli aveugle sur une catégorie au hasard.
    """
    if not website:
        return
    Product = env['product.template']
    Category = env['product.public.category']

    orphaned = Product.search([
        ('website_id', '=', website.id),
        ('public_categ_ids', '=', False),
    ])
    if not orphaned:
        return

    all_cats = Category.search([('website_id', '=', website.id)])
    child_parent_ids = set(all_cats.mapped('parent_id').ids)
    leaf_cats = all_cats.filtered(lambda c: c.id not in child_parent_ids)
    # Les noms les plus longs/précis d'abord, pour ne pas matcher un nom
    # générique court avant un nom plus spécifique qui le contiendrait.
    leaf_cats = leaf_cats.sorted(key=lambda c: -len(c.name))
    leaf_by_name = {c.name: c for c in leaf_cats}

    # CORRECTIF (mot-clé PARTIEL) : le nom complet d'une catégorie
    # n'apparaît presque jamais tel quel dans le nom d'un produit (ex:
    # 'Chargeurs & Alimentations' ne figure jamais dans "Base chargeur
    # pour TPE Ingenico..."). On ajoute donc une liste de mots-clés
    # PARTIELS -> catégorie cible, à étendre au fur et à mesure des
    # produits orphelins repérés dans les logs. Vérifiés dans l'ordre :
    # le premier mot-clé trouvé dans le nom du produit l'emporte.
    PRODUCT_KEYWORD_CATEGORY = [
        ('chargeur', 'Chargeurs & Alimentations'),
        ('housse', 'Housses & protections'),
        ('protection', 'Housses & protections'),
        ('coque', 'Housses & protections'),
        ('câble', 'Cables'),
        ('cable', 'Cables'),
        ('batterie', 'Batteries TPE'),
    ]

    repaired = 0
    still_unmatched = []
    for p in orphaned:
        pname_lower = p.name.lower()
        match = next(
            (c for c in leaf_cats if c.name and c.name.lower() in pname_lower),
            None,
        )
        if not match:
            for kw, target_name in PRODUCT_KEYWORD_CATEGORY:
                if kw in pname_lower and target_name in leaf_by_name:
                    match = leaf_by_name[target_name]
                    break
        if match:
            p.write({'public_categ_ids': [(6, 0, [match.id])]})
            repaired += 1
        else:
            still_unmatched.append(p.name)

    if repaired:
        _logger.info(
            "_repair_orphaned_categories : %s produit(s) sans catégorie "
            "rattaché(s) automatiquement par mot-clé trouvé dans leur nom.",
            repaired,
        )
    if still_unmatched:
        _logger.warning(
            "_repair_orphaned_categories : %s produit(s) restent SANS "
            "AUCUNE catégorie (aucun mot-clé de catégorie détecté dans "
            "leur nom) -- à catégoriser manuellement en backend : %s",
            len(still_unmatched), still_unmatched,
        )


# Catégories FANTÔMES constatées en conditions réelles : des catégories
# portant le nom EXACT de l'ancien site (probablement créées par une
# manipulation shell antérieure à ce module), séparées de notre propre
# arborescence construite par get_or_create() plus haut dans ce hook.
# Des produits s'y retrouvent bel et bien catégorisés (donc invisibles
# pour _repair_orphaned_categories, qui ne touche que les produits SANS
# aucune catégorie) mais dans la mauvaise branche, jamais affichée
# comme filtre boutique. À compléter au fur et à mesure des découvertes.
STRAY_CATEGORY_ALIASES = {
    'bases chargeur': 'Chargeurs & Alimentations',
}


def _merge_stray_categories(env, website):
    """Fusionne les catégories fantômes listées dans
    STRAY_CATEGORY_ALIASES vers la bonne catégorie de notre arborescence :
    déplace tous leurs produits (et ceux de leurs éventuelles
    sous-catégories) vers la cible, puis archive la catégorie fantôme
    (jamais supprimée, réactivable si besoin — même principe que
    _merge_root_category ci-dessus). Idempotent : sans effet si la
    catégorie fantôme n'existe pas ou plus (déjà fusionnée/archivée).
    """
    if not website:
        return
    Category = env['product.public.category']
    Product = env['product.template']
    # La catégorie CIBLE (celle où tout doit atterrir) doit appartenir
    # explicitement à notre site -- jamais deviner un site absent.
    our_categories = Category.search([('website_id', '=', website.id)])
    by_name = {}
    for c in our_categories:
        by_name.setdefault(c.name.strip().lower(), []).append(c)

    # CORRECTIF : les catégories FANTÔMES elles (celles à fusionner et
    # vider) peuvent avoir été créées SANS website_id du tout par une
    # manipulation shell antérieure -- une recherche strictement scopée
    # à notre site les ratait entièrement, et la fusion ne se déclenchait
    # jamais (constaté en conditions réelles sur 'Bases chargeur'). On
    # élargit donc la recherche des fantômes à website_id in [False, nôtre].
    stray_search_categories = Category.search([('website_id', 'in', [False, website.id])])
    stray_by_name = {}
    for c in stray_search_categories:
        stray_by_name.setdefault(c.name.strip().lower(), []).append(c)

    merged_total = 0
    for stray_name, target_name in STRAY_CATEGORY_ALIASES.items():
        targets = by_name.get(target_name.strip().lower())
        target = targets[0] if targets else None
        if not target:
            continue
        for stray in stray_by_name.get(stray_name, []):
            if stray.id == target.id:
                continue
            tree = stray | Category.search([('id', 'child_of', stray.ids)])
            products = Product.search([
                ('public_categ_ids', 'in', tree.ids),
                ('website_id', '=', website.id),
            ])
            if products:
                for p in products:
                    new_categs = (p.public_categ_ids - tree) | target
                    p.write({'public_categ_ids': [(6, 0, new_categs.ids)]})
                merged_total += len(products)
                _logger.info(
                    "_merge_stray_categories : %s produit(s) déplacé(s) de "
                    "la catégorie fantôme '%s' (id=%s) vers '%s' (id=%s).",
                    len(products), stray.name, stray.id, target.name, target.id,
                )
            # NOTE : product.public.category n'a PAS de champ 'active' dans
            # cette version d'Odoo (contrairement à la plupart des modèles)
            # -- impossible de l'archiver. Sans risque : la catégorie
            # fantôme reste techniquement présente mais totalement vide
            # (tous ses produits viennent d'être déplacés ci-dessus), donc
            # invisible dans les filtres boutique de toute façon.
            _logger.info(
                "_merge_stray_categories : catégorie fantôme '%s' (id=%s) "
                "vidée de ses produits (reste en base, vide, non affichée).",
                stray.name, stray.id,
            )
    if merged_total:
        _logger.info(
            "_merge_stray_categories : %s produit(s) au total réconciliés "
            "vers l'arborescence officielle.",
            merged_total,
        )


def _merge_root_category(env, website, old_name, target_category):
    """RÉCUPÈRE une ancienne catégorie racine préexistante (nom
    différent de la nôtre, ex: 'Informatique') en migrant TOUS ses
    produits vers notre catégorie cible (ex: 'Informatique & Réseaux').
    Rien n'est perdu : chaque produit garde ses catégories existantes
    ET gagne la nouvelle.

    CORRECTIF : product.public.category n'a PAS de champ 'active' dans
    cette version d'Odoo (contrairement à la plupart des modèles) --
    un vieil appel à old.write({'active': False}) ici plantait toute la
    mise à jour du module dès qu'une catégorie 'old_name' existait
    vraiment (ValueError: Invalid field ...active). Retiré : la
    catégorie reste en base mais vide (tous ses produits migrés
    ci-dessus), donc invisible dans les filtres boutique de toute façon.
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
    _logger.info(
        "Catégorie '%s' (id=%s) RÉCUPÉRÉE dans '%s' : %s produit(s) "
        "migré(s), rien perdu. Ancienne catégorie laissée en base, vide.",
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


def _setup_languages(env, website):
    """Active fr_FR + en_US sur le site Exocoms et fixe fr_FR comme
    langue par défaut du site.

    CORRECTIF : ce bloc vivait uniquement dans post_init_hook, donc ne
    se rejouait JAMAIS sur les mises à jour suivantes (post_migrate_hook
    ne le faisait pas). Sur un environnement où _get_website() retrouve
    le site existant par son ID mémorisé (jamais recréé), post_init_hook
    ne s'exécute qu'une seule fois dans la vie du site — si les langues
    n'étaient pas encore posées correctement à ce moment-là (ou ont été
    perdues depuis, ex: site dupliqué depuis un snapshot antérieur à ce
    réglage), plus rien ne les corrige ensuite. Extrait en fonction
    séparée pour être appelée aussi depuis post_migrate_hook, comme le
    reste des réglages "maintenus à chaque update" dans ce fichier."""
    lang_fr = env['res.lang'].search([('code', '=', 'fr_FR')], limit=1)
    if not lang_fr:
        env['res.lang']._activate_lang('fr_FR')
        lang_fr = env['res.lang'].search([('code', '=', 'fr_FR')], limit=1)

    lang_en = env['res.lang'].search([('code', '=', 'en_US')], limit=1)
    if not lang_en:
        env['res.lang']._activate_lang('en_US')
        lang_en = env['res.lang'].search([('code', '=', 'en_US')], limit=1)

    if website and lang_fr:
        website.write({'language_ids': [(5, 0, 0)]})
        website.write({
            'default_lang_id': lang_fr.id,
            'language_ids': [(4, lang_fr.id)] + ([(4, lang_en.id)] if lang_en else []),
        })

    return lang_fr, lang_en


def _setup_demo_avis(env, website):
    """Sème quelques avis publiés de démonstration, UNIQUEMENT si le
    site n'en a encore aucun (jamais de doublon, jamais d'écrasement
    d'avis réels déjà déposés par de vrais clients). Contenu repris des
    anciens témoignages codés en dur dans features_section, maintenant
    stockés comme de vrais enregistrements exocoms.avis pour que la
    home et /avis affichent du contenu réel dès le lancement plutôt
    qu'un carousel vide."""
    if not website:
        return
    Avis = env['exocoms.avis'].sudo()
    if Avis.search_count([('website_id', '=', website.id)]):
        return

    from datetime import date, timedelta
    today = date.today()
    demo_avis = [
        ('Nadia K.', 5, "Déployé 30 TPE en une semaine pour notre réseau de pharmacies. Zéro panne, zéro stress. Un partenaire de confiance.", 'TPE Ingenico', 3),
        ('Alexandre C.', 5, "Notre hôtel utilise leurs terminaux depuis 3 saisons. La remontée des paiements en temps réel a changé notre gestion.", 'TPE Portable', 7),
        ('Rachid L.', 5, "J'avais des doutes au départ mais l'onboarding était impeccable. Mon équipe a été formée en 2h chrono.", '', 12),
        ('Fatima D.', 4, "Le support répond en moins d'une heure même le samedi. Pour une chaîne de 18 restaurants c'est indispensable.", 'Caisse Enregistreuse', 15),
        ('Julien M.', 5, "Migration de notre ancien système sans aucune interruption de caisse. Impressionnant pour un centre commercial.", '', 20),
        ('Sofia B.', 5, "Excellent rapport qualité prix. Les terminaux SUNMI sont robustes et le logiciel est intuitif pour mes vendeurs.", 'Terminal SUNMI', 25),
    ]
    for name, rating, comment, product, days_ago in demo_avis:
        avis = Avis.with_context(lang='fr_FR').create({
            'name': name,
            'rating': rating,
            'comment': comment,
            'product': product,
            'date': today - timedelta(days=days_ago),
            'state': 'published',
            'website_id': website.id,
        })
        # Traduit tout de suite vers l'anglais (contenu rédigé en
        # français) — best-effort, cf. action_translate_missing() :
        # si le réseau est indisponible pendant l'install, l'avis reste
        # simplement affiché en français côté anglais pour l'instant.
        avis.with_context(lang='fr_FR').action_translate_missing()
    _logger.info("%s avis de démonstration créés pour le site %s.", len(demo_avis), website.name)


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
    # Extrait dans _setup_languages() (voir plus haut) pour pouvoir
    # être rejoué aussi depuis post_migrate_hook.
    lang_fr, lang_en = _setup_languages(env, website)

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
    # CORRECTIF : ce réglage n'existait auparavant que dans
    # post_migrate_hook() — qui ne s'exécute JAMAIS automatiquement
    # ('post_migrate' n'est pas un hook reconnu par Odoo, cf. notes
    # plus haut dans ce fichier). Résultat : après un rebuild ou une
    # installation fraîche, la boutique retombait sur le design natif
    # "Vignettes" au lieu de "Chips". On l'applique donc ici aussi,
    # dans post_init_hook, qui lui s'exécute réellement à l'install.
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
        _logger.exception("Échec écriture shop_opt_products_design_classes (post_init_hook)")

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

    # === MIGRATION DEPUIS LE SITE PRÉEXISTANT — appelée ICI, après la
    # construction complète de l'arborescence, pour que la
    # correspondance par nom de catégorie fonctionne correctement. ===
    _migrate_products_from_legacy_site(env, website)

    # === RATTRAPAGE PRODUITS SANS CATÉGORIE — au cas où la migration
    # ci-dessus n'ait pas trouvé de correspondance pour certains (voir
    # la docstring de la fonction). ===
    _repair_orphaned_categories(env, website)

    # === FUSION DES CATÉGORIES FANTÔMES — produits déjà catégorisés
    # mais dans une branche parallèle (ex: 'Bases chargeur' au lieu de
    # 'Chargeurs & Alimentations'), donc invisibles à _repair_orphaned_
    # categories() qui ne cible que les produits SANS aucune catégorie. ===
    _merge_stray_categories(env, website)

    # === RATTACHEMENT DES ATTRIBUTS/FILTRES MONÉTIQUE AUX PRODUITS —
    # appelé ICI, après que la catégorie 'Monétique' et ses produits
    # (natifs + migrés) existent tous. Voir la docstring de la
    # fonction : sans ce rattachement, les filtres restent invisibles
    # dans la boutique malgré des attributs bien créés. ===
    _attach_monetique_attributes_to_products(env, website)

    # === AVIS DE DÉMONSTRATION — uniquement si le site n'en a aucun ===
    _setup_demo_avis(env, website)

    # NOTE : Le footer et le copyright sont gérés par
    # views/templates/footer.xml (templates custom_footer et
    # custom_copyright, inherit_id="website.layout"). Ils sont
    # désormais scopés au site Exocoms via _scope_layout_views(),
    # appelée juste après _setup_theme_assets() ci-dessus.


def post_migrate_hook(env):
    """S'exécute à chaque update du module — strictement scopé à notre site."""
    website = _get_website(env)
    company = _get_company(env)

    # Langues maintenues à chaque update — voir _setup_languages() :
    # sur un site retrouvé par son ID mémorisé (jamais recréé),
    # post_init_hook ne se relance pas après le tout premier install,
    # donc c'est ce hook qui doit garantir que fr_FR/en_US restent
    # actives sur le site (cause probable si l'anglais ne s'affiche
    # jamais malgré des traductions .po correctes).
    lang_fr, lang_en = _setup_languages(env, website)

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

    # === RATTRAPAGE PRODUITS SANS CATÉGORIE — CRUCIAL ICI (pas juste
    # dans post_init_hook) : c'est la SEULE façon de réparer, sur une
    # base déjà installée, des produits déjà migrés vers notre site
    # avant ce correctif mais restés sans catégorie (ex: bug 'Housses
    # et protections' vs 'Housses & protections'). Un rejeu de
    # _migrate_products_from_legacy_site() seul ne les revoit plus, car
    # leur website_id a déjà changé -- voir la docstring de
    # _repair_orphaned_categories(). Idempotent, sans risque à chaque
    # update. ===
    _repair_orphaned_categories(env, website)

    # Fusion des catégories fantômes maintenue à chaque update aussi
    # (voir _merge_stray_categories) — indispensable pour rattraper la
    # production actuelle sans rebuild.
    _merge_stray_categories(env, website)

    # Rattachement aux produits maintenu à chaque update aussi — un
    # nouveau produit Monétique ajouté/migré entre deux updates doit
    # récupérer les mêmes filtres que les autres, sans y toucher s'il
    # les a déjà (voir la fonction : idempotent, ne réécrase jamais
    # une sélection de valeurs déjà affinée manuellement).
    _attach_monetique_attributes_to_products(env, website)

    # Avis de démonstration — ne fait rien si le site en a déjà (réels
    # ou démo), donc sans danger de relancer ceci à chaque update.
    _setup_demo_avis(env, website)

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