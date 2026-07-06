# -*- coding: utf-8 -*-
from odoo import _, api, fields, models

CHORUS_PRO_URL = "https://portail.chorus-pro.gouv.fr"


class AccountMove(models.Model):
    _inherit = 'account.move'

    is_public_entity_partner = fields.Boolean(
        related='partner_id.commercial_partner_id.is_public_entity',
        string="Client entité publique",
    )
    engagement_juridique = fields.Char(
        string="N° d'engagement juridique",
        copy=False,
        help="Numéro d'engagement juridique (bon de commande) de l'entité "
             "publique, à renseigner lors du dépôt sur Chorus Pro.",
    )
    chorus_service_code = fields.Char(
        string="Code service (Chorus Pro)",
        compute='_compute_chorus_service_code',
        store=True,
        readonly=False,
        copy=False,
    )
    chorus_sent = fields.Boolean(
        string="Déposée sur Chorus Pro",
        copy=False,
        tracking=True,
    )
    chorus_sent_date = fields.Datetime(
        string="Date de dépôt Chorus Pro",
        copy=False,
    )

    @api.depends('partner_id')
    def _compute_chorus_service_code(self):
        for move in self:
            if not move.chorus_service_code:
                move.chorus_service_code = (
                    move.partner_id.commercial_partner_id.chorus_service_code
                )

    def action_mark_chorus_sent(self):
        """Marquer la facture comme déposée sur Chorus Pro."""
        for move in self:
            move.write({
                'chorus_sent': True,
                'chorus_sent_date': fields.Datetime.now(),
            })
            move.message_post(
                body=_("Facture déposée sur Chorus Pro le %s.",
                       fields.Datetime.now().strftime('%d/%m/%Y %H:%M')),
            )
        return True

    def action_reset_chorus_sent(self):
        """Annuler le marquage de dépôt Chorus Pro."""
        self.write({'chorus_sent': False, 'chorus_sent_date': False})
        return True

    def action_open_chorus_pro(self):
        """Ouvrir le portail Chorus Pro dans un nouvel onglet."""
        return {
            'type': 'ir.actions.act_url',
            'url': CHORUS_PRO_URL,
            'target': 'new',
        }
