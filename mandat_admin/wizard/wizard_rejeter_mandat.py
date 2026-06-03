# -*- coding: utf-8 -*-
from odoo import fields, models, _
from odoo.exceptions import UserError


class WizardRejeterMandat(models.TransientModel):
    _name = 'wizard.rejeter.mandat'
    _description = 'Assistant de rejet de mandat'

    mandat_id = fields.Many2one('mandat.administratif', string='Mandat', required=True)
    motif_rejet = fields.Text(string='Motif de rejet', required=True)

    def action_confirmer_rejet(self):
        self.ensure_one()
        if not self.motif_rejet:
            raise UserError(_("Veuillez saisir un motif de rejet."))
        self.mandat_id.write({
            'state': 'rejete',
            'motif_rejet': self.motif_rejet,
        })
        self.mandat_id.message_post(
            body=_("Mandat <b>rejeté</b>. Motif : %s") % self.motif_rejet,
            subtype_xmlid='mail.mt_note',
        )
        return {'type': 'ir.actions.act_window_close'}
