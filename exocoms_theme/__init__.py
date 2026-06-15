# -*- coding: utf-8 -*-
from . import controllers
from . import models


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

    # === SITE WEB + RÉSEAUX SOCIAUX ===
    website = env['website'].search([], limit=1)
    if website:
        website.write({
            'name': 'Exocoms Group',
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

    # === FORCER FR PAR DÉFAUT SUR TOUTES LES PAGES ===
    public_user = env.ref('base.public_user', raise_if_not_found=False)
    if public_user and lang_fr:
        public_user.with_context(no_recompute=True).write({'lang': 'fr_FR'})

    public_partner = env.ref('base.public_partner', raise_if_not_found=False)
    if public_partner and lang_fr:
        public_partner.with_context(no_recompute=True).write({'lang': 'fr_FR'})

    params = env['ir.config_parameter'].sudo()
    params.set_param('web.base.lang', 'fr_FR')
    params.set_param('website.default_lang_id', str(lang_fr.id) if lang_fr else 'fr_FR')
    params.set_param('website.lang_redirect_from_browser', False)

    try:
        if website:
            website.sudo().write({
                'user_lang_redirect': False,
            })
    except Exception:
        pass

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
    # === DÉSACTIVER REDIRECTION LANGUE ===
    try:
        if website:
            website.write({
                'default_lang_id': lang_fr.id,
                # Empêche Odoo de rediriger vers /fr/
                'user_lang_redirect': False,
            })
    except Exception:
        pass
    # === MENUS — FR par défaut + traduction EN ===
    menus_update = {
        5: ('Accueil', '/',              'Home'),
        7: ('Boutique', '/shop',         'Shop'),
        6: ('Nos services', '/services', 'Our Services'),
    }
    for menu_id, (name_fr, url, name_en) in menus_update.items():
        menu = env['website.menu'].browse(menu_id)
        if not menu.exists():
            continue
        menu.with_context(lang='fr_FR').write({'name': name_fr, 'url': url})
        if lang_en:
            menu.with_context(lang='en_US').write({'name': name_en})

    # Supprimer les menus indésirables
    menus_to_delete = [9, 10, 11, 12, 13]
    for menu_id in menus_to_delete:
        menu = env['website.menu'].browse(menu_id)
        if menu.exists():
            menu.unlink()

    # === PROFIL DROPDOWN — Mon compte ===
    account_view = env['ir.ui.view'].browse(637)
    if account_view.exists():
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

    # === FOOTER CONTENT ===
    footer_content = """
        <section class="s_text_block pt40 pb16" data-snippet="s_text_block" data-name="Container">
            <div class="container">
                <div class="row">
                    <t t-if="request.env.lang == 'fr_FR'">
                        <div class="col-lg-5 pt24 pb24">
                            <h5>&#192; propos de nous</h5>
                            <p style="font-size: 14px;">Nous sommes une &#233;quipe de passionn&#233;s dont le but est d&#39;am&#233;liorer la vie de chacun gr&#226;ce &#224; des produits disruptifs. Nous commercialisons d&#39;excellents produits pour r&#233;soudre vos probl&#232;mes commerciaux. Nos produits sont con&#231;us pour les petites et moyennes entreprises ainsi que les franchises d&#233;sireuses d&#39;optimiser leurs performances.</p>
                        </div>
                        <div class="col-lg-2 pt24 pb24">
                            <h5>Liens utiles</h5>
                            <ul class="list-unstyled" style="font-size: 14px;">
                                <li><a href="/" style="font-size: 14px;">Page d&#39;accueil</a></li>
                                <li><a href="/services" style="font-size: 14px;">Nos services</a></li>
                                <li><a href="/mentions-legales" style="font-size: 14px;">Mentions l&#233;gales</a></li>
                            </ul>
                        </div>
                        <div class="col-lg-4 offset-lg-1 pt24 pb24">
                            <h5>Contact</h5>
                            <p style="font-size: 14px;">Une question, un projet ou besoin d&#39;un accompagnement ?</p>
                            <ul class="list-unstyled" style="font-size: 14px;">
                                <li><i class="fa fa-comment fa-fw me-2"></i><a href="/contactus" style="font-size: 14px;">Contactez-nous</a></li>
                                <li><i class="fa fa-envelope fa-fw me-2"></i><a href="mailto:contact@exocoms.fr" style="font-size: 14px;">contact@exocoms.fr</a></li>
                                <li><i class="fa fa-phone fa-fw me-2"></i><a href="tel:+33184793755" style="font-size: 14px;">+33 (0)1 84 79 37 55</a></li>
                            </ul>
                            <div class="s_social_media text-start o_not_editable" data-snippet="s_social_media" data-name="Social Media">
                                <a href="/website/social/facebook" class="s_social_media_facebook" target="_blank" aria-label="Facebook"><i class="fa fa-facebook rounded-circle shadow-sm"></i></a>
                                <a href="/website/social/twitter" class="s_social_media_twitter" target="_blank" aria-label="X"><i class="fa fa-twitter rounded-circle shadow-sm"></i></a>
                                <a href="/website/social/linkedin" class="s_social_media_linkedin" target="_blank" aria-label="LinkedIn"><i class="fa fa-linkedin rounded-circle shadow-sm"></i></a>
                                <a href="/" aria-label="Accueil"><i class="fa fa-home rounded-circle shadow-sm"></i></a>
                            </div>
                        </div>
                    </t>
                    <t t-else="">
                        <div class="col-lg-5 pt24 pb24">
                            <h5>About us</h5>
                            <p style="font-size: 14px;">We are a team of passionate people whose goal is to improve everyone&#39;s life through disruptive products. We market excellent products to solve your business problems. Our products are designed for small and medium businesses as well as franchises looking to optimize their performance.</p>
                        </div>
                        <div class="col-lg-2 pt24 pb24">
                            <h5>Useful links</h5>
                            <ul class="list-unstyled" style="font-size: 14px;">
                                <li><a href="/" style="font-size: 14px;">Home</a></li>
                                <li><a href="/services" style="font-size: 14px;">Our services</a></li>
                                <li><a href="/mentions-legales" style="font-size: 14px;">Legal notice</a></li>
                            </ul>
                        </div>
                        <div class="col-lg-4 offset-lg-1 pt24 pb24">
                            <h5>Contact</h5>
                            <p style="font-size: 14px;">A question, a project or need support?</p>
                            <ul class="list-unstyled" style="font-size: 14px;">
                                <li><i class="fa fa-comment fa-fw me-2"></i><a href="/contactus" style="font-size: 14px;">Contact us</a></li>
                                <li><i class="fa fa-envelope fa-fw me-2"></i><a href="mailto:contact@exocoms.fr" style="font-size: 14px;">contact@exocoms.fr</a></li>
                                <li><i class="fa fa-phone fa-fw me-2"></i><a href="tel:+33184793755" style="font-size: 14px;">+33 (0)1 84 79 37 55</a></li>
                            </ul>
                            <div class="s_social_media text-start o_not_editable" data-snippet="s_social_media" data-name="Social Media">
                                <a href="/website/social/facebook" class="s_social_media_facebook" target="_blank" aria-label="Facebook"><i class="fa fa-facebook rounded-circle shadow-sm"></i></a>
                                <a href="/website/social/twitter" class="s_social_media_twitter" target="_blank" aria-label="X"><i class="fa fa-twitter rounded-circle shadow-sm"></i></a>
                                <a href="/website/social/linkedin" class="s_social_media_linkedin" target="_blank" aria-label="LinkedIn"><i class="fa fa-linkedin rounded-circle shadow-sm"></i></a>
                                <a href="/" aria-label="Home"><i class="fa fa-home rounded-circle shadow-sm"></i></a>
                            </div>
                        </div>
                    </t>
                </div>
            </div>
        </section>"""

    # === FOOTER — clé robuste Odoo 19 ===
    footer_view = env['ir.ui.view'].search([
        ('key', '=', 'website.footer_custom')
    ], limit=1)

    if footer_view:
        try:
            footer_view.write({
                'priority': 1000,
                'active': True,
                'arch': """
<data inherit_id="website.layout" name="Default" active="True">
    <xpath expr="//div[@id='footer']" position="replace">
        <div id="footer" class="oe_structure oe_structure_solo border text-break"
             t-ignore="true" t-if="not no_footer"
             style="--box-border-left-width: 0px; --box-border-right-width: 0px;">
""" + footer_content + """
        </div>
    </xpath>
</data>
"""})
        except Exception:
            try:
                footer_view.write({'arch': """
<data inherit_id="website.layout" name="Default" active="True">
    <xpath expr="//div[hasclass('oe_structure_solo')]" position="replace">
        <div id="footer" class="oe_structure oe_structure_solo border text-break"
             t-ignore="true" t-if="not no_footer"
             style="--box-border-left-width: 0px; --box-border-right-width: 0px;">
""" + footer_content + """
        </div>
    </xpath>
</data>
"""})
            except Exception:
                pass

    # === COPYRIGHT ===
    copyright_view = env['ir.ui.view'].search([
        ('key', '=', 'website.footer_copyright_company_name')
    ], limit=1)

    if copyright_view:
        try:
            copyright_view.write({'arch': """
<data>
    <xpath expr="//span[hasclass('o_footer_copyright_name')]" position="replace">
        <span class="o_footer_copyright_name me-2 small">
            <t t-if="request.env.lang == 'fr_FR'">
                Copyright &#169; 2026 Exocoms Group. Tous droits r&#233;serv&#233;s.
            </t>
            <t t-else="">
                Copyright &#169; 2026 Exocoms Group. All rights reserved.
            </t>
        </span>
    </xpath>
</data>
"""})
        except Exception:
            pass


def post_migrate_hook(env):
    """S'exécute à chaque update du module"""
    website = env['website'].search([], limit=1)
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