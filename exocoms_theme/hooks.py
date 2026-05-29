from odoo import api, SUPERUSER_ID


def post_init_hook(env):
    """Initialise le footer natif Odoo avec les données Exocoms Group"""

    website = env['website'].search([], limit=1)
    if not website:
        return

    # Mise à jour de la company
    company = env['res.company'].search([], limit=1)
    if company:
        company.write({
            'name': 'Exocoms Group',
            'email': 'contact@exocoms.fr',
            'phone': '+33 (0)1 84 79 37 55',
            'street': 'Paris',
            'country_id': env.ref('base.fr').id,
        })

    # Mise à jour des réseaux sociaux du site
    website.write({
        'name': 'Exocoms Group',
        'social_facebook': 'https://www.facebook.com/exocoms',
        'social_twitter': 'https://twitter.com/exocoms',
        'social_linkedin': 'https://www.linkedin.com/company/exocoms',
    })

    # Mise à jour du footer natif Odoo
    footer_view = env['ir.ui.view'].search([
        ('key', '=', 'website.footer_custom'),
        ('website_id', '=', website.id),
    ], limit=1)

    footer_arch = """
<div id="footer" class="oe_structure oe_structure_solo">
    <section class="s_text_block pt40 pb16">
        <div class="container">
            <div class="row">
                <div class="col-lg-5 pt24 pb24">
                    <h5>À propos de nous</h5>
                    <p>Nous sommes une équipe de passionnés dont le but est d&#39;améliorer la vie de chacun grâce à des produits disruptifs. Nous commercialisons d&#39;excellents produits pour résoudre vos problèmes commerciaux. Nos produits sont conçus pour les petites et moyennes entreprises ainsi que les franchises désireuses d&#39;optimiser leurs performances.</p>
                </div>
                <div class="col-lg-2 pt24 pb24">
                    <h5>Liens utiles</h5>
                    <ul class="list-unstyled">
                        <li><a href="/">Page d&#39;accueil</a></li>
                        <li><a href="/services">Nos services</a></li>
                        <li><a href="/mentions-legales">Mentions légales</a></li>
                    </ul>
                </div>
                <div class="col-lg-4 offset-lg-1 pt24 pb24">
                    <h5>Contact</h5>
                    <p>Une question, un projet ou besoin d&#39;un accompagnement ?</p>
                    <ul class="list-unstyled">
                        <li><i class="fa fa-comment fa-fw me-2"></i><a href="/contactus">Contactez-nous</a></li>
                        <li><i class="fa fa-envelope fa-fw me-2"></i><a href="mailto:contact@exocoms.fr">contact@exocoms.fr</a></li>
                        <li><i class="fa fa-phone fa-fw me-2"></i><a href="tel:+33184793755">+33 (0)1 84 79 37 55</a></li>
                    </ul>
                    <div class="s_social_media text-start">
                        <a href="https://www.facebook.com/exocoms" target="_blank" aria-label="Facebook" class="s_social_media_facebook">
                            <i class="fa fa-facebook rounded-circle shadow-sm"></i>
                        </a>
                        <a href="https://twitter.com/exocoms" target="_blank" aria-label="X" class="s_social_media_twitter">
                            <i class="fa fa-twitter rounded-circle shadow-sm"></i>
                        </a>
                        <a href="https://www.linkedin.com/company/exocoms" target="_blank" aria-label="LinkedIn" class="s_social_media_linkedin">
                            <i class="fa fa-linkedin rounded-circle shadow-sm"></i>
                        </a>
                        <a href="/" aria-label="Accueil">
                            <i class="fa fa-home rounded-circle shadow-sm"></i>
                        </a>
                    </div>
                </div>
            </div>
        </div>
    </section>
</div>
"""

    if footer_view:
        footer_view.write({'arch': footer_arch})
    else:
        # Crée le footer custom pour ce site
        env['ir.ui.view'].create({
            'name': 'Footer Exocoms',
            'type': 'qweb',
            'key': 'website.footer_custom',
            'website_id': website.id,
            'inherit_id': env.ref('website.footer_custom').id,
            'arch': footer_arch,
        })

    # Copyright
    env['ir.config_parameter'].sudo().set_param(
        'website.copyright', '© 2026 Exocoms Group. Tous droits réservés.'
    )