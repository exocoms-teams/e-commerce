# -*- coding: utf-8 -*-
import logging
import os
import base64

from .constants import (
    CONFIG_WEBSITE_ID_KEY,
    CONFIG_ASSETS_FIX_KEY,
    CONFIG_LOGO_APPLIED_KEY,
    CONFIG_DOMAIN_LIVE_KEY,
    COMPANY_NAME,
    WEBSITE_NAME,
    WEBSITE_DOMAIN,
    LOGO_PATH,
    THEME_ASSETS,
    SCOPED_VIEW_XML_IDS,
    RESETTABLE_VIEW_XML_IDS,
    SHOP_CATEGORIES,
    SHOP_SUBCATEGORIES,
    SHOP_FILTER_ATTRIBUTES,
    SHOP_DESIGN_CLASSES,
)

_logger = logging.getLogger(__name__)


def _get_company(env):
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
    Users = env['res.users'].sudo()
    admin_group_xmlid = 'base.group_system'
    if not env.ref(admin_group_xmlid, raise_if_not_found=False):
        _logger.warning(
            "capsule_house_theme: groupe %s introuvable — accès société "
            "non accordé automatiquement aux administrateurs.",
            admin_group_xmlid,
        )
        return

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
        'company_id': company.id,
    })
    ICP.set_param(CONFIG_WEBSITE_ID_KEY, str(website.id))
    _logger.info(
        "capsule_house_theme: nouveau site créé id=%s, mémorisé dans '%s'.",
        website.id, CONFIG_WEBSITE_ID_KEY,
    )
    return website


def _setup_pricelist(env, website, company):
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
    return env['res.users'].search([
        ('active', '=', True),
        ('share', '=', False),
        ('login', 'not in', ['__system__']),
    ], order='id asc', limit=1)


def _setup_livechat(env, website):
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

    channel.write({
        'header_background_color': '#1F2421',
        'title_color': '#FFFFFF',
        'button_background_color': '#C1694F',
        'button_text_color': '#FFFFFF',
    })

    if not channel.rule_ids:
        env['im_livechat.channel.rule'].create({
            'channel_id': channel.id,
            'regex_url': '/',
            'action': 'display_button',
            'sequence': 10,
        })

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


def _set_logo(env, website):
    ICP = env['ir.config_parameter'].sudo()
    if ICP.get_param(CONFIG_LOGO_APPLIED_KEY) == '1':
        return
    try:
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
    if website.homepage_url:
        _logger.info(
            "capsule_house_theme: homepage_url du site id=%s vidée "
            "(était %r) — l'accueil est servi directement sur '/' "
            "depuis la 19.0.1.0.57.", website.id, website.homepage_url,
        )
        website.write({'homepage_url': False})


def _setup_domain(env, website):
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


def _reset_customized_views(env):
    View = env['ir.ui.view'].sudo()
    reset_count = 0
    for xml_id in RESETTABLE_VIEW_XML_IDS:
        view = env.ref(xml_id, raise_if_not_found=False)
        if not view:
            continue
        try:
            view.reset_arch(mode='hard')
            reset_count += 1
        except Exception:
            _logger.exception(
                "capsule_house_theme: échec du reset_arch sur %s", xml_id,
            )
    _logger.info(
        "capsule_house_theme: %d vue(s) réalignée(s) sur l'arch du "
        "module (reset_arch hard).", reset_count,
    )


def _clean_demo_data(env, website):
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
        "capsule_house_theme: %d catégorie(s) boutique top-level "
        "synchronisée(s) pour le site id=%s.", len(categories), website.id,
    )

    reparented = 0
    for parent_name, child_names in SHOP_SUBCATEGORIES.items():
        parent = categories.get(parent_name)
        if not parent:
            _logger.warning(
                "capsule_house_theme: catégorie parente '%s' introuvable — "
                "sous-catégories %s non rattachées.", parent_name, child_names,
            )
            continue
        for child_name in child_names:
            domain = [('name', '=', child_name)]
            if has_website_field:
                domain += ['|', ('website_id', '=', website.id), ('website_id', '=', False)]
            child = Category.search(domain, limit=1)
            if child:
                to_write = {}
                if child.parent_id.id != parent.id:
                    to_write['parent_id'] = parent.id
                if has_website_field and not child.website_id:
                    to_write['website_id'] = website.id
                if to_write:
                    child.write(to_write)
                    reparented += 1
            else:
                vals = {'name': child_name, 'parent_id': parent.id}
                if has_website_field:
                    vals['website_id'] = website.id
                child = Category.create(vals)
                reparented += 1
            categories[child_name] = child
    if reparented:
        _logger.info(
            "capsule_house_theme: %d sous-catégorie(s) rattachée(s)/créée(s) "
            "sous leur gamme parente pour le site id=%s (%s) — retirées des "
            "onglets de premier niveau de /shop.",
            reparented, website.id, SHOP_SUBCATEGORIES,
        )
    return categories


def _setup_shop_display(env, website):
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
    Menu = env['website.menu'].sudo()
    entries = [
        ('Accueil', '/', 10),
        ('Tous les pods', '/shop', 20),
    ]
    sequence = 30
    if 'Accessoires' in categories:
        entries.append((
            'Accessoires', '/shop/category/%d' % categories['Accessoires'].id, sequence,
        ))
        sequence += 10
    entries.append(('Promotions', '/shop?promotions=1', sequence))
    sequence += 10
    entries.append(('Avis clients', '/avis', sequence))

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

    stray_menus = website.menu_id.child_id.filtered(
        lambda m: m.id not in kept_menu_ids and m.url not in known_urls
    )
    if stray_menus:
        _logger.info(
            "capsule_house_theme: suppression de %d menu(s) par défaut non "
            "reconnu(s) sur le site id=%s : %s.",
            len(stray_menus), website.id, stray_menus.mapped('name'),
        )
        stray_menus.unlink()


def _setup_shop_filters(env):
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