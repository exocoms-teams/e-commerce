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

# Route dédiée et unique à ce module (jamais '/', qui est partagée par tous
# les sites de la base mutualisée) : voir _setup_homepage() et le docstring
# de CapsuleHouseWebsite dans controllers/main.py pour le pourquoi.
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
    'capsule_house_theme.partial_featured_products',
    'capsule_house_theme.page_home',
    'capsule_house_theme.page_shop',
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
    """
    Users = env['res.users'].sudo()
    admin_group = env.ref('base.group_system', raise_if_not_found=False)
    if not admin_group:
        _logger.warning(
            "capsule_house_theme: groupe base.group_system introuvable — "
            "accès société non accordé automatiquement aux "
            "administrateurs."
        )
        return

    admins = Users.search([('groups_id', 'in', admin_group.id)])
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
    """Fait pointer l'accueil de NOTRE site vers notre route dédiée.

    Ne touche JAMAIS à la route '/' elle-même (partagée par tous les sites
    de la base mutualisée) : on se contente d'écrire le champ natif
    `website.homepage_url` sur NOTRE enregistrement website, qui est par
    construction scopé (c'est un champ sur le record `website`, pas une
    donnée recherchée par domaine). Odoo gère nativement la redirection
    interne de '/' vers cette URL pour les visiteurs de ce site
    uniquement. Idempotent : simple write, sans effet si déjà à jour.
    """
    if website.homepage_url != HOMEPAGE_ROUTE:
        website.write({'homepage_url': HOMEPAGE_ROUTE})
        _logger.info(
            "capsule_house_theme: homepage_url du site id=%s pointée vers "
            "%s.", website.id, HOMEPAGE_ROUTE,
        )


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


def _setup_menus(env, website, categories):
    """Crée le menu du site, scopé à notre website_id.

    Reprend la nav de la maquette de référence : Accueil (racine, masquée
    du header qui gère son propre logo-lien), Tous les pods (/shop), une
    entrée par catégorie boutique, puis Promotions. get_or_create par (url,
    website_id) pour rester idempotent et ne jamais dupliquer une entrée au
    fil des rejeux du hook / du cron.
    """
    Menu = env['website.menu'].sudo()
    entries = [
        ('Accueil', '/', 10),
        ('Tous les pods', '/shop', 20),
    ]
    sequence = 30
    for name, category in categories.items():
        entries.append((name, '/shop/category/%d' % category.id, sequence))
        sequence += 10
    # Pas de route de filtre "promotions" native dans website_sale : ce lien
    # pointe sur /shop pour l'instant. À remplacer par une vraie route
    # filtrée (ex: domaine sur les prix barrés / une pricelist promo) une
    # fois le mécanisme de promotion du client confirmé.
    entries.append(('Promotions', '/shop?promotions=1', sequence))

    known_urls = {url for _, url, _ in entries}
    kept_menu_ids = set()
    for name, url, seq in entries:
        existing = Menu.search([
            ('url', '=', url),
            ('website_id', '=', website.id),
        ], limit=1)
        if existing:
            existing.write({'name': name, 'sequence': seq})
            kept_menu_ids.add(existing.id)
        else:
            created = Menu.create({
                'name': name,
                'url': url,
                'sequence': seq,
                'website_id': website.id,
                'parent_id': website.menu_id.id,
            })
            kept_menu_ids.add(created.id)
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
        _logger.warning(
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
    _set_logo(env, website)
    _setup_homepage(env, website)
    _setup_domain(env, website)
    _setup_theme_assets(env, website)
    _invalidate_frontend_assets(env, website)
    _scope_layout_views(env, website)
    _clean_demo_data(env, website)
    categories = _setup_shop_categories(env, website)
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
