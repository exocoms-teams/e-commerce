# -*- coding: utf-8 -*-
from . import controllers
from . import models

WEBSITE_NAME = 'Exocoms Group'
OUR_URLS = ['/', '/shop', '/services', '/infogerance']


def _get_website(env):
    """Retourne le website Exocoms Group — par nom, jamais par ID."""
    website = env['website'].search([('name', '=', WEBSITE_NAME)], limit=1)
    if not website:
        website = env['website'].search([], limit=1)
    return website


def _clean_demo_data(env, website):
    """Nettoie les données de démo créées automatiquement par Odoo.
    - Supprime "My Website 2" (site fantôme de démo)
    - Supprime les doublons de menus sur notre site
    Compatible avec tous les autres modules — cible uniquement les données de démo connues.
    """
    if not website:
        return

    # 1. Supprimer le site fantôme de démo Odoo — ciblé par nom exact
    ghost = env['website'].search([
        ('name', '=', 'My Website 2'),
        ('id', '!=', website.id),
    ], limit=1)
    if ghost:
        env['website.menu'].search([('website_id', '=', ghost.id)]).unlink()
        env['website.page'].search([('website_id', '=', ghost.id)]).unlink()
        ghost.unlink()

    # 2. Rattacher les menus orphelins (sans website_id) qui sont les nôtres
    orphans = env['website.menu'].search([
        ('website_id', '=', False),
        ('url', 'in', OUR_URLS),
    ])
    if orphans:
        orphans.write({'website_id': website.id})

    # 3. Supprimer les doublons de menus sur notre site
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
    """Gestion complète des menus."""
    if not website:
        return

    # Nettoyer d'abord les données de démo et doublons
    _clean_demo_data(env, website)

    root_menu = env['website.menu'].search([
        ('parent_id', '=', False),
        ('website_id', '=', website.id),
    ], limit=1)

    menus = [
        ('/',         'Accueil',      'Home',         1),
        ('/shop',     'Boutique',     'Shop',         2),
        ('/services', 'Nos services', 'Our Services', 3),
        ('/infogerance', 'Infogérance', 'Managed IT', 4),
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


def _setup_monetique_attributes(env, lang_en):
    """Crée les attributs/filtres boutique pour la gamme Monétique.

    Idempotent — recherche par nom (en langue de base fr_FR) avant
    création, ne touche jamais aux attributs déjà existants/personnalisés.

    Traduction : chaque nom (attribut + valeur) est écrit explicitement
    en fr_FR, puis en en_US si cette langue est active sur le site —
    exactement la même logique que _get_or_create_menu. Comme ça, le
    filtre change correctement de libellé quand le visiteur bascule la
    langue du site (FR <-> EN), sans dépendre de la langue de session
    de l'utilisateur qui exécute le hook.
    """
    attr_model = env['product.attribute']
    value_model = env['product.attribute.value']

    def get_or_create_attribute(name_fr, name_en, display_type='radio', sequence=10):
        # Recherche toujours faite avec le nom fr_FR comme référence stable
        attr = attr_model.with_context(lang='fr_FR').search(
            [('name', '=', name_fr)], limit=1
        )
        if not attr:
            attr = attr_model.with_context(lang='fr_FR').create({
                'name': name_fr,
                'display_type': display_type,   # 'radio', 'select', 'pills', 'color'
                'create_variant': 'no_variant',  # n'affecte pas les variantes produit
                'sequence': sequence,
            })
        else:
            attr.with_context(lang='fr_FR').write({'sequence': sequence})

        # Traduction explicite — jamais d'identifiant traduisible dans une recherche
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

    # --- Forfait DATA par TPE / TPE Data Plan ---
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

    # --- Nombre de chèques par mois / Cheques per month ---
    # ⚠️ valeurs provisoires en attendant confirmation des vraies tranches
    cheques = get_or_create_attribute(
        'Nombre de chèques par mois', 'Cheques per month',
        display_type='select', sequence=2
    )
    for i, (fr, en) in enumerate([
        ('5', '5'), ('10', '10'), ('15', '15'),
        ('20', '20'), ('30', '30'), ('50', '50'),
    ]):
        get_or_create_value(cheques, fr, en, sequence=i)

    # --- Garantie / Warranty ---
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

    # --- Type de modèle / Model type ---
    modele = get_or_create_attribute(
        'Type de modèle', 'Model type',
        display_type='select', sequence=4
    )
    for i, (fr, en) in enumerate([
        ('1 x RS232', '1 x RS232'),
        ('2 x RS232', '2 x RS232'),
    ]):
        get_or_create_value(modele, fr, en, sequence=i)

    # --- Quantité / Quantity ---
    quantite = get_or_create_attribute(
        'Quantité', 'Quantity',
        display_type='pills', sequence=5
    )
    for i, (fr, en) in enumerate([
        ('5', '5'), ('15', '15'), ('20', '20'), ('50', '50'),
    ]):
        get_or_create_value(quantite, fr, en, sequence=i)


def post_init_hook(env):
    """Initialise les données Exocoms Group"""

    # === COMPANY ===
    company = env['res.company'].search([], limit=1)
    if company:
        company.write({
            'name': 'Exocoms Group',
            'email': 'contact@exocoms.fr',
            'phone': '+33 (0)1 84 79 37 55',
            'country_id': env.ref('base.fr').id,
        })

    # === SITE WEB — on nomme le site en premier pour que _get_website() fonctionne ===
    website = env['website'].search([], limit=1)
    if website:
        website.write({
            'name': WEBSITE_NAME,
            'social_facebook': 'https://www.facebook.com/exocoms',
            'social_twitter': 'https://twitter.com/exocoms',
            'social_linkedin': 'https://www.linkedin.com/company/exocoms',
        })

    # === LANGUES — Français + Anglais ===
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
    # Le public_user doit être en fr_FR pour qu'Odoo serve le français par défaut sur "/".
    # Sans ça, Odoo détecte en_US sur le public_user et force l'anglais sur la page d'accueil.
    public_user = env.ref('base.public_user', raise_if_not_found=False)
    if public_user and lang_fr:
        public_user.with_context(no_recompute=True).write({'lang': 'fr_FR'})

    public_partner = env.ref('base.public_partner', raise_if_not_found=False)
    if public_partner and lang_fr:
        public_partner.with_context(no_recompute=True).write({'lang': 'fr_FR'})

    params = env['ir.config_parameter'].sudo()
    params.set_param('web.base.lang', 'fr_FR')
    params.set_param('website.default_lang_id', str(lang_fr.id) if lang_fr else 'fr_FR')

    # Charger les traductions françaises officielles Odoo
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

    # === PROFIL DROPDOWN — Mon compte (recherche par clé, pas par ID) ===
    account_view = env['ir.ui.view'].search([
        ('key', '=', 'portal.user_dropdown_link_account'),
    ], limit=1)
    if not account_view:
        account_view = env['ir.ui.view'].search([
            ('name', 'ilike', 'Link to frontend portal'),
            ('inherit_id.key', '=', 'portal.user_dropdown'),
        ], limit=1)
    if account_view and account_view.exists():
        account_view.write({'arch': """
<data name="Link to frontend portal" inherit_id="portal.user_dropdown">
    <xpath expr="//*[@id='o_logout_divider']" position="before">
        <a href="/my/home" role="menuitem" class="dropdown-item ps-3">
            <i class="fa fa-fw fa-id-card-o me-1 small text-primary-emphasis"></i>
            My Account
        </a>
    </xpath>
</data>
"""})

    # === DÉCONNEXION — supprimer la vue custom ===
    existing = env['ir.ui.view'].search([
        ('name', '=', 'Exocoms Logout FR')
    ], limit=1)
    if existing:
        existing.unlink()

    # === DESIGN BOUTIQUE — Chips par défaut ===
    try:
        grid_views = env['ir.ui.view'].search([
            ('key', 'like', 'website_sale.products'),
            ('type', '=', 'qweb'),
        ])
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
                pass
    except Exception:
        pass

    # === PUBLIER TOUS LES PRODUITS ===
    try:
        env["product.template"].search([("is_published", "=", False)]).write({"is_published": True})
    except Exception:
        pass

    # === CRÉER TOUTE LA STRUCTURE DE CATÉGORIES ===
    cat = env['product.public.category']

    demo_names = [
        'Desks', 'Furnitures', 'Boxes', 'Drawers',
        'Cabinets', 'Bins', 'Lamps', 'All',
        'Indoor', 'Outdoor', 'Multimedia',
    ]
    cats_demo = cat.search([('name', 'in', demo_names)])
    if cats_demo:
        cats_demo.unlink()

    def get_or_create(name, parent=None, seq=10):
        domain = [('name', '=', name)]
        if parent:
            domain.append(('parent_id', '=', parent.id))
        else:
            domain.append(('parent_id', '=', False))
        c = cat.search(domain, limit=1)
        if not c:
            vals = {'name': name, 'sequence': seq}
            if parent:
                vals['parent_id'] = parent.id
            c = cat.create(vals)
        return c

    informatique = get_or_create('Informatique & Réseaux', seq=1)
    monetique_root = get_or_create('Monétique', seq=2)
    telecom = get_or_create('Télécom', seq=3)

    monetique_sub = cat.search([
        ('name', '=', 'Monetique'), ('parent_id', '=', False)
    ], limit=1)
    if monetique_sub:
        monetique_sub.write({'parent_id': monetique_root.id, 'sequence': 1})

    pdv = cat.search([
        ('name', 'ilike', 'Point de vente'), ('parent_id', '=', False)
    ], limit=1)
    if pdv:
        pdv.write({'parent_id': monetique_root.id, 'sequence': 2})

    get_or_create('Matériel & Informatique Générale', informatique, seq=1)
    get_or_create('Réseaux & Infrastructure', informatique, seq=2)
    get_or_create('Communication & Vidéo', informatique, seq=3)

    monetique = cat.search([
        ('name', '=', 'Monetique'), ('parent_id', '=', monetique_root.id)
    ], limit=1)
    if not monetique:
        monetique = cat.create({
            'name': 'Monetique',
            'parent_id': monetique_root.id,
            'sequence': 1
        })

    caisse = get_or_create('Caisse Enregistreuse', monetique_root, seq=3)
    get_or_create('Distributeur automatique', monetique_root, seq=4)
    monnaie = get_or_create('Monnaie & Chèque', monetique_root, seq=5)
    crypto = get_or_create('Crypto', monetique_root, seq=6)
    accessoires = get_or_create('Accessoires', monetique_root, seq=7)
    consommables = get_or_create('Consommables', monetique_root, seq=8)
    services = get_or_create('Services', monetique_root, seq=9)

    tpe_fixe = get_or_create('TPE Fixe', monetique, seq=1)
    get_or_create('INGENICO', tpe_fixe)
    get_or_create('PAX', tpe_fixe)

    tpe_portable = get_or_create('TPE Portable', monetique, seq=2)
    get_or_create('INGENICO', tpe_portable)
    get_or_create('PAX', tpe_portable)
    get_or_create('UROVO', tpe_portable)
    get_or_create('SUNMI', tpe_portable)

    tpe_mobile = get_or_create('TPE Mobile', monetique, seq=3)
    get_or_create('INGENICO', tpe_mobile)
    get_or_create('PAX', tpe_mobile)
    get_or_create('UROVO', tpe_mobile)

    tpe_sante = get_or_create('TPE Santé', monetique, seq=4)
    get_or_create('INGENICO', tpe_sante)
    get_or_create('PAX', tpe_sante)

    pin_pad = get_or_create('PIN Pad', monetique, seq=5)
    get_or_create('INGENICO', pin_pad)
    get_or_create('PAX', pin_pad)

    logiciels_tpe = get_or_create('Logiciels TPE', monetique, seq=6)
    get_or_create('Ingenico', logiciels_tpe)
    get_or_create('Verifone', logiciels_tpe)
    get_or_create('Pax', logiciels_tpe)

    passerelles = get_or_create('Passerelles', monetique, seq=7)
    get_or_create('Passerelle IP', passerelles)
    get_or_create('Passerelle 3G/4G', passerelles)

    caisse_tactile = get_or_create('Caisse Tactile', caisse, seq=1)
    sunmi_cat = get_or_create('SUNMI', caisse_tactile)
    get_or_create('Sunmi D3 80mm', sunmi_cat)
    get_or_create('SUNMI D3 PRO', sunmi_cat)
    get_or_create('SUNMI D3 MINI', sunmi_cat)
    get_or_create('SUNMI T3', sunmi_cat)
    get_or_create('PAX', caisse_tactile)

    imprimante = get_or_create('Imprimante', caisse, seq=2)
    get_or_create('Imprimante Ticket', imprimante)
    get_or_create('Imprimante Etiquette', imprimante)

    get_or_create('Kiosques', caisse, seq=3)
    logiciels_caisse = get_or_create('Logiciels', caisse, seq=4)
    get_or_create('Cybersécurité', logiciels_caisse)
    get_or_create('Accessoires', caisse, seq=5)
    get_or_create('Consommables', caisse, seq=6)
    get_or_create('Services', caisse, seq=7)

    get_or_create('Scanner de Chèque', monnaie)
    get_or_create('Lecteur de Chèque', monnaie)
    detecteurs = get_or_create('Détecteurs et Compteuses', monnaie)
    get_or_create('Compteuse de Pièces', detecteurs)
    get_or_create('Compteuse de Billets', detecteurs)
    get_or_create('Détecteurs', detecteurs)

    get_or_create('ATM', crypto)
    get_or_create('Logiciel ATM', crypto)
    get_or_create('Formation ATM', crypto)

    get_or_create('Batteries TPE', accessoires)
    chargeurs = get_or_create('Chargeurs & Alimentations', accessoires)
    get_or_create('INGENICO', chargeurs)
    get_or_create('PAX', chargeurs)
    cables = get_or_create('Cables', accessoires)
    get_or_create('INGENICO', cables)
    get_or_create('VERIFONE', cables)
    get_or_create('Housses & protections', accessoires)
    get_or_create('Pièces détachées', accessoires)

    get_or_create('Monetique', consommables)
    get_or_create('Pitney Bowes', consommables)
    get_or_create('Panini', consommables)
    get_or_create("DOC'UP", consommables)
    get_or_create('Autres', consommables)

    get_or_create('Monetique', services)
    get_or_create('Caisse Enregistreuse', services)
    get_or_create('Pièces Détachées', services)

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

    # NOTE : Le footer et le copyright sont désormais gérés par
    # views/templates/footer.xml (templates custom_footer et
    # custom_copyright, inherit_id="website.layout"), pas ici.
    # Cela évite le bug de validation XPath rencontré avec
    # position="replace" en Python, et garantit l'affichage sur
    # TOUTES les pages du site de façon déclarative et stable.


def post_migrate_hook(env):
    """S'exécute à chaque update du module"""
    website = _get_website(env)
    lang_en = env['res.lang'].search([('code', '=', 'en_US')], limit=1)

    # Menus maintenus + nettoyage démo à chaque update
    _setup_menus(env, website, lang_en)

    # Attributs/filtres maintenus + traduction à chaque update
    _setup_monetique_attributes(env, lang_en)

    if website:
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
            pass