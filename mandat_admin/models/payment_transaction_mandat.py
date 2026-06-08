# -*- coding: utf-8 -*-
from odoo import models, fields, api, _
from odoo.exceptions import UserError


class PaymentTransactionMandat(models.Model):
    _inherit = 'payment.transaction'

    mandat_id = fields.Many2one(
        'mandat.administratif',
        string='Mandat administratif lié',
        readonly=True,
        copy=False,
    )

    def _get_specific_rendering_values(self, processing_values):
        res = super()._get_specific_rendering_values(processing_values)
        if self.provider_code != 'mandat_administratif':
            return res
        return res

    def _process_notification_data(self, notification_data):
        super()._process_notification_data(notification_data)
        if self.provider_code != 'mandat_administratif':
            return
        self._set_pending()

    def action_create_mandat(self):
        """Créer un mandat administratif lié à cette transaction."""
        self.ensure_one()
        if self.provider_code != 'mandat_administratif':
            raise UserError(_("Cette action n'est disponible que pour les paiements par mandat administratif."))
        if self.mandat_id:
            raise UserError(_("Un mandat est déjà lié à cette transaction."))

        # Récupérer la commande liée
        sale_order = self.sale_order_ids[:1] if self.sale_order_ids else False

        mandat_vals = {
            'objet': self.reference,
            'montant_ttc': self.amount,
            'collectivite_id': self.env.company.id,
            'ordonnateur_id': self.env.user.id,
        }

        if sale_order and sale_order.partner_id:
            mandat_vals['creancier_id'] = sale_order.partner_id.id

        mandat = self.env['mandat.administratif'].create(mandat_vals)
        self.mandat_id = mandat.id

        return {
            'type': 'ir.actions.act_window',
            'name': _('Mandat Administratif'),
            'res_model': 'mandat.administratif',
            'res_id': mandat.id,
            'view_mode': 'form',
            'target': 'current',
        }


class MandatAdministratif(models.Model):
    _inherit = 'mandat.administratif'

    transaction_id = fields.Many2one(
        'payment.transaction',
        string='Transaction de paiement liée',
        readonly=True,
        copy=False,
    )

    def action_marquer_paye(self):
        """Override : quand le mandat est payé, confirmer la transaction et la commande."""
        res = super().action_marquer_paye()
        for rec in self:
            if rec.transaction_id and rec.transaction_id.state != 'done':
                rec.transaction_id._set_done()
                # Confirmer les commandes liées
                for order in rec.transaction_id.sale_order_ids:
                    if order.state in ('draft', 'sent'):
                        order.action_confirm()
        return res
