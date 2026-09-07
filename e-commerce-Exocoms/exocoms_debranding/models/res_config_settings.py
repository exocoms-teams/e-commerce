# -*- coding: utf-8 -*-
from odoo import fields, models

from ..hooks import DEFAULT_BRAND, DEFAULT_EXCLUDED_MODULES, DEFAULT_LOGO_URL, rebrand


class ResConfigSettings(models.TransientModel):
    _inherit = "res.config.settings"

    # --- Par société -------------------------------------------------------
    debranding_name = fields.Char(
        related="company_id.debranding_name",
        string="Nom de marque",
        readonly=False,
    )
    debranding_url = fields.Char(
        related="company_id.debranding_url",
        string="Site web",
        readonly=False,
    )
    debranding_documentation_url = fields.Char(
        related="company_id.debranding_documentation_url",
        string="URL documentation",
        readonly=False,
    )
    debranding_support_url = fields.Char(
        related="company_id.debranding_support_url",
        string="URL support",
        readonly=False,
    )
    debranding_logo_url = fields.Char(
        related="company_id.debranding_logo_url",
        string="URL du logo",
        readonly=False,
    )
    debranding_theme_color = fields.Char(
        related="company_id.debranding_theme_color",
        string="Couleur de thème (PWA)",
        readonly=False,
    )
    debranding_logo = fields.Binary(
        related="company_id.logo",
        string="Logo de la société",
        readonly=False,
    )
    

    # --- Global à la base --------------------------------------------------
    debranding_multi_company = fields.Boolean(
        string="Marque par société",
        config_parameter="debranding.multi_company",
        help="Activé : les templates rendent la marque de la société courante. "
             "Désactivé : la marque par défaut est écrite en dur dans les "
             "templates (plus robuste, une seule marque pour toute la base).",
    )
    debranding_default_name = fields.Char(
        string="Marque par défaut",
        config_parameter="debranding.name",
        default=DEFAULT_BRAND,
        help="Utilisée par les sociétés qui n'ont pas de nom de marque propre.",
    )
    debranding_default_url = fields.Char(
        string="Site web par défaut",
        config_parameter="debranding.url",
    )
    debranding_default_logo_url = fields.Char(
        string="URL de logo par défaut",
        config_parameter="debranding.logo_url",
        default=DEFAULT_LOGO_URL,
    )
    debranding_web_app_name = fields.Char(
        string="Nom de l'application (PWA)",
        config_parameter="web.web_app_name",
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

    def set_values(self):
        res = super().set_values()
        rebrand(self.env)
        return res

    def action_debranding_rescan(self):
        """Re-scanne et ré-applique les patchs (après installation de modules)."""
        self.ensure_one()
        rebrand(self.env)
        return {"type": "ir.actions.client", "tag": "reload"}
