# -*- coding: utf-8 -*-
from lxml import etree

from odoo import fields, models


class MatelasNewsletterWizard(models.TransientModel):
    """Assistant déclenché par un bouton (Email Marketing > Générer la
    newsletter Matelas) qui construit automatiquement un brouillon
    d'email reprenant les nouveautés/produits mis en avant sur le site
    """
    _name = 'matelas.newsletter.wizard'
    _description = "Générer la newsletter Matelas"

    def action_generate(self):
        self.ensure_one()
        env = self.env

        mailing_list = env.ref('matelas.newsletter_mailing_list', raise_if_not_found=False)
        # Compatibilité avec les bases où l’identifiant externe serait absent.
        if not mailing_list:
            mailing_list = env['mailing.list'].search(
                [('name', '=', 'Newsletter Matelas')], limit=1)
        if not mailing_list:
            mailing_list = env['mailing.list'].create({'name': 'Newsletter Matelas'})

        nouveaute_tag = env.ref('matelas.product_tag_nouveaute', raise_if_not_found=False)
        products = env['product.template']
        if nouveaute_tag:
            products = env['product.template'].search([
                ('is_published', '=', True),
                ('product_tag_ids', 'in', nouveaute_tag.ids),
            ], limit=6)
        # Fallback volontaire : la seconde requête n’est exécutée que si
        # aucun produit publié avec le tag Nouveauté n’a été trouvé.
        if not products:
            products = env['product.template'].search([
                ('is_published', '=', True),
            ], order='create_date desc', limit=6)

        base_url = env['ir.config_parameter'].sudo().get_param('web.base.url') or ''

        # Rendu du corps via le template QWeb dédié (data/mail_template.xml),
        # plutôt que par concaténation de chaînes Python. Le champ body_html
        # du mail.template contient un fragment QWeb "inerte" (t-foreach,
        # t-esc, t-attf-src...) : on le parse puis on le fait rendre par le
        # moteur QWeb d'Odoo avec les valeurs voulues.
        template = env.ref('matelas.mail_template_newsletter')
        arch = etree.fromstring(template.body_html.encode())
        body_html = str(env['ir.qweb']._render(arch, {
            'products': products,
            'base_url': base_url,
        }))

        today = fields.Date.today()
        mailing = env['mailing.mailing'].create({
            'name': "Newsletter Matelas - %s" % today,
            'subject': template.subject,
            'body_arch': body_html,
            'body_html': body_html,
            'contact_list_ids': [(6, 0, mailing_list.ids)],
        })

        return {
            'type': 'ir.actions.act_window',
            'res_model': 'mailing.mailing',
            'view_mode': 'form',
            'res_id': mailing.id,
            'target': 'current',
        }
