# -*- coding: utf-8 -*-
from markupsafe import Markup, escape

from odoo import api, fields, models

DEBRAND_FIELDS = {
    "debrand_mode",
    "debrand_promo_text",
    "debrand_brand_name",
    "debrand_brand_url",
    "debrand_logo",
    "debrand_show_logo",
    "debrand_logo_height",
    "debrand_backend",
}


class ResCompany(models.Model):
    """Paramètres de marque blanche, par société.

    Multi-société : chaque société (donc chaque client hébergé) a sa propre
    marque, son propre logo et son propre lien.
    """

    _inherit = "res.company"

    debrand_mode = fields.Selection(
        selection=[
            ("replace", "Remplacer par notre marque"),
            ("remove", "Supprimer sans rien afficher"),
        ],
        string="Mentions Odoo",
        default="replace",
        required=True,
        help="« Remplacer » conserve le bloc d'origine (position, alignement, "
             "style) et n'en change que le contenu. « Supprimer » retire le bloc.",
    )
    debrand_promo_text = fields.Char(
        string="Texte d'accroche",
        default="Propulsé par",
        help="Texte affiché avant la marque. Laisser vide pour n'afficher que "
             "le logo et/ou le nom.",
    )
    debrand_brand_name = fields.Char(
        string="Nom de marque",
        help="Laisser vide pour utiliser le nom de la société.",
    )
    debrand_brand_url = fields.Char(
        string="Lien de la marque",
        help="Laisser vide pour utiliser le site web de la société. "
             "Vide également côté société : le nom n'est pas cliquable.",
    )
    debrand_show_logo = fields.Boolean(
        string="Afficher le logo",
        default=False,
    )
    debrand_logo = fields.Image(
        string="Logo de marque",
        max_width=512,
        max_height=512,
        help="Utilisé dans les pieds de page du portail, des e-mails et des "
             "rapports PDF. Un PNG à fond transparent d'environ 200x50 px "
             "donne le meilleur rendu.",
    )
    debrand_logo_height = fields.Integer(
        string="Hauteur du logo (px)",
        default=16,
    )
    debrand_backend = fields.Boolean(
        string="Débrander le back-office",
        default=True,
        help="Remplace « Odoo » par la marque dans le titre de l'onglet du "
             "navigateur et retire les entrées Documentation / Support / "
             "Compte Odoo du menu utilisateur.",
    )

    # ------------------------------------------------------------------
    # Helpers
    # ------------------------------------------------------------------
    def _debrand_name(self):
        self.ensure_one()
        return self.debrand_brand_name or self.name or ""

    def _debrand_url(self):
        self.ensure_one()
        return self.debrand_brand_url or self.website or ""

    def _debrand_logo_url(self):
        """URL absolue du logo (indispensable pour les e-mails et les PDF)."""
        self.ensure_one()
        base = self.env["ir.config_parameter"].sudo().get_param("web.base.url", "")
        unique = int(self.write_date.timestamp()) if self.write_date else 0
        return "%s/exocoms_brand/logo?company=%s&unique=%s" % (base, self.id, unique)

    def _debrand_snippet(self):
        """Bloc HTML de marque injecté à la place de la mention Odoo.

        Retourne ``None`` en mode « supprimer » ou si rien n'est à afficher.
        """
        self.ensure_one()
        if self.debrand_mode != "replace":
            return None

        name = self._debrand_name()
        url = self._debrand_url()
        parts = []

        if self.debrand_promo_text:
            parts.append(escape(self.debrand_promo_text))

        inner = []
        if self.debrand_show_logo and self.debrand_logo:
            height = self.debrand_logo_height or 16
            inner.append(Markup(
                '<img src="%s" alt="%s" style="height:%dpx;width:auto;'
                'vertical-align:middle;border:0;"/>'
            ) % (self._debrand_logo_url(), name, height))
        if name and not (self.debrand_show_logo and self.debrand_logo):
            inner.append(escape(name))

        if not inner:
            return None

        label = Markup(" ").join(inner)
        if url:
            body = Markup(
                '<a href="%s" target="_blank" rel="noopener" '
                'style="color:inherit;text-decoration:none;font-weight:600;">%s</a>'
            ) % (url, label)
        else:
            body = Markup('<span style="font-weight:600;">%s</span>') % label

        parts.append(body)
        return Markup(" ").join(parts)

    # ------------------------------------------------------------------
    # Invalidation des caches
    # ------------------------------------------------------------------
    @api.model_create_multi
    def create(self, vals_list):
        companies = super().create(vals_list)
        self.env.registry.clear_cache()
        return companies

    def write(self, vals):
        result = super().write(vals)
        if DEBRAND_FIELDS & set(vals):
            self.env.registry.clear_cache()
        return result
