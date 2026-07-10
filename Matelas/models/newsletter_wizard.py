# -*- coding: utf-8 -*-
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

        mailing_list = env.ref('Matelas.newsletter_mailing_list', raise_if_not_found=False)
        if not mailing_list:
            mailing_list = env['mailing.list'].search(
                [('name', '=', 'Newsletter Matelas')], limit=1)
        if not mailing_list:
            mailing_list = env['mailing.list'].create({'name': 'Newsletter Matelas'})

        nouveaute_tag = env.ref('Matelas.product_tag_nouveaute', raise_if_not_found=False)
        products = env['product.template']
        if nouveaute_tag:
            products = env['product.template'].search([
                ('is_published', '=', True),
                ('product_tag_ids', 'in', nouveaute_tag.ids),
            ], limit=6)
        if not products:
            products = env['product.template'].search([
                ('is_published', '=', True),
            ], order='create_date desc', limit=6)

        base_url = env['ir.config_parameter'].sudo().get_param('web.base.url') or ''

        rows = ''
        for product in products:
            rows += '''
            <tr>
              <td style="padding:16px 0;border-bottom:1px solid #f1efec;">
                <table width="100%%" cellpadding="0" cellspacing="0">
                  <tr>
                    <td style="width:110px;vertical-align:top;">
                      <img src="%(base_url)s/web/image/product.template/%(id)s/image_256"
                           style="width:100px;border-radius:8px;" alt="%(name)s"/>
                    </td>
                    <td style="padding-left:16px;vertical-align:top;">
                      <div style="font-weight:700;font-size:16px;color:#3a3a3a;">%(name)s</div>
                      <div style="color:#c96b4a;font-weight:700;font-size:15px;margin:4px 0;">%(price).2f &#8364;</div>
                      <a href="%(base_url)s%(url)s" style="color:#c96b4a;text-decoration:none;font-weight:600;">Découvrir &#8594;</a>
                    </td>
                  </tr>
                </table>
              </td>
            </tr>
            ''' % {
                'base_url': base_url,
                'id': product.id,
                'name': product.name,
                'price': product.list_price,
                'url': product.website_url,
            }

        body_html = '''
        <table width="100%%" cellpadding="0" cellspacing="0" style="max-width:600px;margin:0 auto;font-family:Arial,sans-serif;">
          <tr><td style="text-align:center;padding:24px 0;">
            <h1 style="color:#3a3a3a;margin-bottom:4px;">MATELAS</h1>
            <p style="color:#c96b4a;font-weight:700;letter-spacing:2px;margin:0;">NOS NOUVEAUTÉS</p>
          </td></tr>
          %(rows)s
          <tr><td style="text-align:center;padding:24px 0;color:#9a9a9a;font-size:12px;">
            Vous recevez cet email car vous êtes inscrit à la newsletter Matelas.
          </td></tr>
        </table>
        ''' % {'rows': rows}

        today = fields.Date.today()
        mailing = env['mailing.mailing'].create({
            'name': "Newsletter Matelas - %s" % today,
            'subject': 'Découvrez nos nouveautés Matelas',
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
