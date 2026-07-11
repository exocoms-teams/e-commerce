# -*- coding: utf-8 -*-
from odoo import fields, models


class ResConfigSettings(models.TransientModel):
    _inherit = 'res.config.settings'

    chorus_api_active = fields.Boolean(
        related='company_id.chorus_api_active', readonly=False)
    chorus_api_mode = fields.Selection(
        related='company_id.chorus_api_mode', readonly=False)
    chorus_piste_client_id = fields.Char(
        related='company_id.chorus_piste_client_id', readonly=False)
    chorus_piste_client_secret = fields.Char(
        related='company_id.chorus_piste_client_secret', readonly=False)
    chorus_technical_login = fields.Char(
        related='company_id.chorus_technical_login', readonly=False)
    chorus_technical_password = fields.Char(
        related='company_id.chorus_technical_password', readonly=False)
    chorus_flux_syntax = fields.Selection(
        related='company_id.chorus_flux_syntax', readonly=False)

    def action_test_chorus_connection(self):
        return self.company_id.action_test_chorus_connection()
