# -*- coding: utf-8 -*-
from odoo import models, fields

class ResConfigSettings(models.TransientModel):
    _inherit = 'res.config.settings'

    oa_ingram_api_url = fields.Char(
        string='Ingram Micro API URL', 
        config_parameter='oa_beauty_theme.ingram_api_url',
        default='https://api.ingrammicro.com:443/sandbox'
    )
    oa_ingram_client_id = fields.Char(
        string='Ingram Micro Client ID', 
        config_parameter='oa_beauty_theme.ingram_client_id',
        help="L'identifiant fourni (ex: contact@exocoms.fr)"
    )
    oa_ingram_client_secret = fields.Char(
        string='Ingram Micro Client Secret', 
        config_parameter='oa_beauty_theme.ingram_client_secret',
        help="Le code d'accès (ex: OdooJira2026@)"
    )
    oa_ingram_import_as_draft = fields.Boolean(
        string='Import as Draft',
        config_parameter='oa_beauty_theme.ingram_import_as_draft',
        default=True,
        help="If checked, imported products will not be published on the website automatically."
    )
