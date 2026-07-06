# -*- coding: utf-8 -*-
from odoo import _, fields, models

CHORUS_PRO_URL = "https://portail.chorus-pro.gouv.fr"


class AccountMove(models.Model):
    _inherit = 'account.move'

    is_public_entity_partner = fields.Boolean(
        related='partner_id.commercial_partner_id.is_public_entity',
        string="Client entité publique",
    )
    engagement_juridique = fields.Char(string="N° d'engagement juridique", copy=False)
    chorus_service_code  = fields.Char(string="Code service (Chorus Pro)", copy=False)
    chorus_sent          = fields.Boolean(string="Déposée sur Chorus Pro", copy=False, tracking=True)
    chorus_sent_date     = fields.Datetime(string="Date de dépôt Chorus Pro", copy=False)

    def action_mark_chorus_sent(self):
        for move in self:
            move.write({'chorus_sent': True, 'chorus_sent_date': fields.Datetime.now()})
            move.message_post(body=_("Facture déposée sur Chorus Pro le %s.", fields.Datetime.now().strftime('%d/%m/%Y %H:%M')))
        return True

    def action_reset_chorus_sent(self):
        self.write({'chorus_sent': False, 'chorus_sent_date': False})
        return True

    def action_open_chorus_pro(self):
        return {'type': 'ir.actions.act_url', 'url': CHORUS_PRO_URL, 'target': 'new'}
