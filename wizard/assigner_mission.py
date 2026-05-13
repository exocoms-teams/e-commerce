# -*- coding: utf-8 -*-
from odoo import models, fields, api, _
from odoo.exceptions import UserError


class AssignerMissionWizard(models.TransientModel):
    """Wizard pour assigner rapidement un intervenant à une ou plusieurs missions."""
    _name = 'sinistre.assigner.mission.wizard'
    _description = 'Assigner Intervenant'

    mission_ids = fields.Many2many(
        'sinistre.mission',
        string='Missions',
        default=lambda self: self.env.context.get('active_ids', []),
    )
    intervenant_id = fields.Many2one(
        'sinistre.intervenant',
        string='Intervenant',
        required=True,
        domain=[('actif', '=', True), ('disponible', '=', True)],
    )
    date_rdv = fields.Datetime(string='Date RDV', required=True)
    note = fields.Text(string='Message à l\'intervenant')

    def action_assigner(self):
        if not self.mission_ids:
            raise UserError(_("Aucune mission sélectionnée."))

        for mission in self.mission_ids:
            mission.write({
                'intervenant_id': self.intervenant_id.id,
                'date_rdv': self.date_rdv,
                'state': 'rdv_planifie',
            })
            mission.message_post(
                body=_(f"Mission assignée à {self.intervenant_id.name}. RDV le {self.date_rdv}. {self.note or ''}"),
                subtype_xmlid='mail.mt_note',
            )

        return {'type': 'ir.actions.act_window_close'}
