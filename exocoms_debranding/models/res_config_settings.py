# -*- coding: utf-8 -*-
from odoo import fields, models

from ..hooks import DEFAULT_BRAND, DEFAULT_EXCLUDED_MODULES, rebrand


class ResConfigSettings(models.TransientModel):
    _inherit = "res.config.settings"

    debranding_name = fields.Char(
        string="Nom de marque",
        config_parameter="debranding.name",
        default=DEFAULT_BRAND,
        help="Remplace « Odoo » dans le titre des pages, les dialogues d'erreur "
             "et les liens « Powered by ».",
    )
    debranding_url = fields.Char(
        string="Site web",
        config_parameter="debranding.url",
        help="Cible des liens rebrandés. Vide : le lien devient du texte simple.",
    )
    debranding_web_app_name = fields.Char(
        string="Nom de l'application (PWA)",
        config_parameter="web.web_app_name",
    )
    debranding_documentation_url = fields.Char(
        string="URL documentation",
        config_parameter="debranding.documentation_url",
        help="Vide : l'entrée « Documentation » est retirée du menu utilisateur.",
    )
    debranding_support_url = fields.Char(
        string="URL support",
        config_parameter="debranding.support_url",
        help="Vide : l'entrée « Support » est retirée du menu utilisateur.",
    )
    debranding_hide_version = fields.Boolean(
        string="Masquer la version du serveur",
        config_parameter="debranding.hide_version",
        help="Les non-administrateurs ne voient plus le numéro de version Odoo.",
    )
    debranding_excluded_modules = fields.Char(
        string="Modules exclus",
        config_parameter="debranding.excluded_modules",
        default=DEFAULT_EXCLUDED_MODULES,
        help="Liste séparée par des virgules. Les liens odoo.com de ces modules "
             "sont fonctionnels (IAP, OAuth, achat de crédits) et ne sont pas réécrits.",
    )
    debranding_logo_url = fields.Char(
        string="URL du logo",
        config_parameter="debranding.logo_url",
        default="/logo.png",
        help="Source utilisée pour les icônes PWA et les visuels Odoo remplacés "
             "dans les templates. Par défaut /logo.png sert le logo de la société.",
    )
    debranding_theme_color = fields.Char(
        string="Couleur de thème (PWA)",
        config_parameter="debranding.theme_color",
        help="Code hexadécimal, ex. #1B4D5E. Vide : couleur Odoo native conservée.",
    )
    debranding_logo = fields.Binary(
        related="company_id.logo",
        string="Logo de la société",
        readonly=False,
    )
    debranding_favicon = fields.Binary(
        related="company_id.favicon",
        string="Favicon",
        readonly=False,
    )

    def set_values(self):
        res = super().set_values()
        rebrand(self.env)
        return res

    def action_debranding_rescan(self):
        """Re-scanne et ré-applique les patchs (après installation de modules)."""
        self.ensure_one()
        rebrand(self.env)
        return {"type": "ir.actions.client", "tag": "reload"}
