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
        langs = [(4, lang_fr.id)]
        if lang_en:
            langs.append((4, lang_en.id))
        website.write({
            'default_lang_id': lang_fr.id,
            'language_ids': langs,
        })

    # === FORCER FR PAR DÉFAUT SUR TOUTES LES PAGES ===
    public_user = env.ref('base.public_user', raise_if_not_found=False)
    if public_user and lang_fr:
        public_user.with_context(no_recompute=True).write({'lang': 'fr_FR'})

    public_partner = env.ref('base.public_partner', raise_if_not_found=False)
    if public_partner and lang_fr:
        public_partner.with_context(no_recompute=True).write({'lang': 'fr_FR'})

    env['ir.config_parameter'].sudo().set_param('web.base.lang', 'fr_FR')

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

    # === PROFIL DROPDOWN — Mon compte (id=637) ===
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

    # === DÉCONNEXION — supprimer la vue custom, Odoo gère nativement FR/EN ===
    existing = env['ir.ui.view'].search([
        ('name', '=', 'Exocoms Logout FR')
    ], limit=1)
    if existing:
        existing.unlink()

    # === FOOTER CONTENT (id=996) ===
    footer_view = env['ir.ui.view'].browse(996)
    if footer_view.exists():
        footer_view.write({'arch': """
<data>
    <xpath expr="//div[@id='footer']" position="replace">
        <div id="footer" class="oe_structure oe_structure_solo border text-break"
             style="--box-border-left-width: 0px; --box-border-right-width: 0px;">
            <section class="s_text_block pt40 pb16" data-snippet="s_text_block" data-name="Container">
                <div class="container">
                    <div class="row">

                        <t t-if="request.env.lang == 'fr_FR'">
                            <div class="col-lg-2 pt24 pb24">
                                <h5>Liens utiles</h5>
                                <ul class="list-unstyled">
                                    <li><a href="/">Page d&#39;accueil</a></li>
                                    <li><a href="/services">Nos services</a></li>
                                    <li><a href="/mentions-legales">Mentions l&#233;gales</a></li>
                                </ul>
                            </div>
                            <div class="col-lg-5 pt24 pb24">
                                <h5>&#192; propos de nous</h5>
                                <p>Nous sommes une &#233;quipe de passionn&#233;s dont le but est d&#39;am&#233;liorer la vie de chacun gr&#226;ce &#224; des produits disruptifs. Nous commercialisons d&#39;excellents produits pour r&#233;soudre vos probl&#232;mes commerciaux. Nos produits sont con&#231;us pour les petites et moyennes entreprises ainsi que les franchises d&#233;sireuses d&#39;optimiser leurs performances.</p>
                            </div>
                            <div class="col-lg-4 offset-lg-1 pt24 pb24">
                                <h5>Contact</h5>
                                <p>Une question, un projet ou besoin d&#39;un accompagnement ?</p>
                                <ul class="list-unstyled">
                                    <li><i class="fa fa-comment fa-fw me-2"></i><a href="/contactus">Contactez-nous</a></li>
                                    <li><i class="fa fa-envelope fa-fw me-2"></i><a href="mailto:contact@exocoms.fr">contact@exocoms.fr</a></li>
                                    <li><i class="fa fa-phone fa-fw me-2"></i><a href="tel:+33184793755">+33 (0)1 84 79 37 55</a></li>
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
                            <div class="col-lg-2 pt24 pb24">
                                <h5>Useful links</h5>
                                <ul class="list-unstyled">
                                    <li><a href="/">Home</a></li>
                                    <li><a href="/services">Our services</a></li>
                                    <li><a href="/mentions-legales">Legal notice</a></li>
                                </ul>
                            </div>
                            <div class="col-lg-5 pt24 pb24">
                                <h5>About us</h5>
                                <p>We are a team of passionate people whose goal is to improve everyone&#39;s life through disruptive products. We market excellent products to solve your business problems. Our products are designed for small and medium businesses as well as franchises looking to optimize their performance.</p>
                            </div>
                            <div class="col-lg-4 offset-lg-1 pt24 pb24">
                                <h5>Contact</h5>
                                <p>A question, a project or need support?</p>
                                <ul class="list-unstyled">
                                    <li><i class="fa fa-comment fa-fw me-2"></i><a href="/contactus">Contact us</a></li>
                                    <li><i class="fa fa-envelope fa-fw me-2"></i><a href="mailto:contact@exocoms.fr">contact@exocoms.fr</a></li>
                                    <li><i class="fa fa-phone fa-fw me-2"></i><a href="tel:+33184793755">+33 (0)1 84 79 37 55</a></li>
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
            </section>
        </div>
    </xpath>
</data>
"""})

    # === COPYRIGHT (id=1012) ===
    copyright_view = env['ir.ui.view'].browse(1012)
    if copyright_view.exists():
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