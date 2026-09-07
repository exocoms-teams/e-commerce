# -*- coding: utf-8 -*-
from odoo import fields, models

from ..hooks import DEFAULT_BRAND, DEFAULT_LOGO_URL

# Champ société -> paramètre système de repli.
_FALLBACKS = {
    "debranding_name": ("debranding.name", DEFAULT_BRAND),
    "debranding_url": ("debranding.url", ""),
    "debranding_documentation_url": ("debranding.documentation_url", ""),
    "debranding_support_url": ("debranding.support_url", ""),
    "debranding_logo_url": ("debranding.logo_url", ""),
    "debranding_theme_color": ("debranding.theme_color", ""),
}


class ResCompany(models.Model):
    _inherit = "res.company"

    debranding_name = fields.Char(
        string="Nom de marque",
        help="Vide : valeur par défaut du paramètre système debranding.name.",
    )
    debranding_url = fields.Char(string="Site web (marque)")
    debranding_documentation_url = fields.Char(string="URL documentation")
    debranding_support_url = fields.Char(string="URL support")
    debranding_logo_url = fields.Char(
        string="URL du logo",
        help="Vide : le logo de cette société est servi via "
             "/web/image/res.company/<id>/logo.",
    )
    debranding_theme_color = fields.Char(string="Couleur de thème (PWA)")
    debranding_favicon = fields.Binary(string="Favicon de la marque")
    
    def _debranding_values(self):
        """Valeurs de marque résolues pour cette société.

        Ordre : champ société -> paramètre système -> valeur codée.
        Utilisable sur un recordset vide (repli sur les paramètres système).
        """
        ICP = self.env["ir.config_parameter"].sudo()
        company = self[:1]
        values = {}
        for field_name, (param, default) in _FALLBACKS.items():
            key = field_name[len("debranding_"):]
            values[key] = (
                (company[field_name] if company else "")
                or ICP.get_param(param)
                or default
            )
        if not values["logo_url"]:
            values["logo_url"] = (
                "/web/image/res.company/%s/logo" % company.id
                if company
                else DEFAULT_LOGO_URL
            )
        # Alias courts consommés par les templates QWeb patchés.
        values["logo"] = values["logo_url"]
        values["company_id"] = company.id if company else False
        return values
