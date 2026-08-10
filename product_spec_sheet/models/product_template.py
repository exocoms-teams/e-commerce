from odoo import _, api, fields, models


class ProductTemplate(models.Model):
    _inherit = 'product.template'

    spec_line_ids = fields.One2many(
        'product.template.spec.line', 'product_tmpl_id',
        string="Caractéristiques",
    )

    def _get_spec_categories(self):
        """Catégories utilisées par ce produit, triées pour l'affichage."""
        self.ensure_one()
        return self.spec_line_ids.category_id.sorted(key=lambda c: (c.sequence, c.name or ''))

    def _get_spec_lines_by_category(self, category):
        """Lignes de caractéristiques d'une catégorie donnée, triées."""
        self.ensure_one()
        return self.spec_line_ids.filtered(
            lambda line: line.category_id == category
        ).sorted(key=lambda line: (line.sequence, line.attribute_id.name or ''))

    def _get_spec_value(self, attribute):
        """Valeur de ce produit pour une caractéristique donnée, ou False si absente."""
        self.ensure_one()
        line = self.spec_line_ids.filtered(lambda l: l.attribute_id == attribute)
        return line.value if line else False

    # ══════════════════════════════════════════════════════════════
    # QUALITÉ DES DONNÉES
    # ══════════════════════════════════════════════════════════════

    spec_count = fields.Integer(
        string="Nb caractéristiques",
        compute="_compute_spec_quality", store=True,
    )
    spec_has_weight = fields.Boolean(
        string="Poids renseigné",
        compute="_compute_spec_quality", store=True,
    )
    spec_has_dimensions = fields.Boolean(
        string="Dimensions renseignées",
        compute="_compute_spec_quality", store=True,
    )
    spec_has_image = fields.Boolean(
        string="Photo renseignée",
        compute="_compute_spec_quality", store=True,
    )
    spec_completeness = fields.Integer(
        string="Complétude (%)",
        compute="_compute_spec_quality", store=True,
        help="Score sur 4 critères : caractéristiques, poids, dimensions, photo.",
    )
    spec_quality_level = fields.Selection(
        [("complete", "Complète"), ("partial", "Partielle"), ("empty", "À compléter")],
        string="Qualité fiche",
        compute="_compute_spec_quality", store=True,
    )
    spec_missing_summary = fields.Char(
        string="Éléments manquants",
        compute="_compute_spec_quality", store=True,
    )

    @api.depends("spec_line_ids", "spec_line_ids.value", "weight", "volume", "image_1920")
    def _compute_spec_quality(self):
        """Calcule le score de complétude de la fiche produit sur 4 critères."""
        dim_attr_names = ("Encombrement", "Dimensions")
        for rec in self:
            rec.spec_count = len(rec.spec_line_ids)

            # Poids : champ Odoo natif ou ligne de caractéristique
            has_weight = bool(rec.weight) and rec.weight > 0
            if not has_weight:
                has_weight = any(
                    l.attribute_id.name == "Poids" and l.value
                    for l in rec.spec_line_ids
                )
            rec.spec_has_weight = has_weight

            # Dimensions : volume Odoo ou ligne Encombrement
            has_dims = bool(rec.volume) and rec.volume > 0
            if not has_dims:
                has_dims = any(
                    l.attribute_id.name in dim_attr_names and l.value
                    for l in rec.spec_line_ids
                )
            rec.spec_has_dimensions = has_dims

            rec.spec_has_image = bool(rec.image_1920)

            criteria = [
                rec.spec_count > 0,
                has_weight,
                has_dims,
                rec.spec_has_image,
            ]
            score = sum(1 for c in criteria if c)
            rec.spec_completeness = int(score / 4 * 100)

            if score == 4:
                rec.spec_quality_level = "complete"
            elif score == 0:
                rec.spec_quality_level = "empty"
            else:
                rec.spec_quality_level = "partial"

            missing = []
            if rec.spec_count == 0:
                missing.append("caractéristiques")
            if not has_weight:
                missing.append("poids")
            if not has_dims:
                missing.append("dimensions")
            if not rec.spec_has_image:
                missing.append("photo")
            rec.spec_missing_summary = ", ".join(missing) if missing else "Complète"

    def action_open_spec_fetch_wizard(self):
        """Ouvre l'assistant de récupération depuis la vue qualité."""
        self.ensure_one()
        return {
            "type": "ir.actions.act_window",
            "res_model": "product.spec.fetch.wizard",
            "view_mode": "form",
            "target": "new",
            "context": {"active_id": self.id, "default_product_tmpl_id": self.id},
        }

    # ══════════════════════════════════════════════════════════════
    # CYCLE DE VIE PRODUIT
    # ══════════════════════════════════════════════════════════════

    lifecycle_state = fields.Selection(
        [
            ("new",        "Nouveauté"),
            ("active",     "Actif"),
            ("eol_soon",   "Fin de commercialisation"),
            ("eol",        "Arrêté"),
            ("obsolete",   "Obsolète"),
        ],
        string="Cycle de vie",
        default="active",
        tracking=True,
        help="Nouveauté : lancement récent.\n"
             "Actif : commercialisé normalement.\n"
             "Fin de commercialisation : encore vendable, stock limité.\n"
             "Arrêté : plus commandable auprès du fabricant.\n"
             "Obsolète : ne doit plus être vendu (certification expirée).",
    )
    lifecycle_eol_date = fields.Date(
        string="Date de fin de commercialisation",
        tracking=True,
        help="Date à partir de laquelle le fabricant ne commercialise plus ce produit.",
    )
    lifecycle_support_end = fields.Date(
        string="Fin de support / certification",
        tracking=True,
        help="Date d'expiration de la certification (PCI PTS, EMV…) ou du support fabricant.",
    )
    lifecycle_replacement_id = fields.Many2one(
        "product.template",
        string="Remplacé par",
        tracking=True,
        domain="[('id','!=',id),('sale_ok','=',True)]",
        help="Produit de remplacement recommandé.",
    )
    lifecycle_note = fields.Text(
        string="Note de cycle de vie",
        help="Précisions affichées au client (raison de l'arrêt, migration conseillée…).",
    )
    lifecycle_warning = fields.Char(
        string="Alerte cycle de vie",
        compute="_compute_lifecycle_warning",
    )
    lifecycle_is_sellable = fields.Boolean(
        string="Encore vendable",
        compute="_compute_lifecycle_warning", store=True,
    )

    @api.depends("lifecycle_state", "lifecycle_eol_date",
                 "lifecycle_support_end", "lifecycle_replacement_id")
    def _compute_lifecycle_warning(self):
        today = fields.Date.context_today(self)
        for rec in self:
            rec.lifecycle_is_sellable = rec.lifecycle_state in ("new", "active", "eol_soon")

            msg = ""
            if rec.lifecycle_state == "obsolete":
                msg = _("Produit obsolète — ne doit plus être vendu.")
            elif rec.lifecycle_state == "eol":
                msg = _("Produit arrêté — plus approvisionnable.")
            elif rec.lifecycle_state == "eol_soon":
                if rec.lifecycle_eol_date:
                    msg = _("Fin de commercialisation prévue le %s.",
                            rec.lifecycle_eol_date.strftime("%d/%m/%Y"))
                else:
                    msg = _("Fin de commercialisation annoncée.")
            elif rec.lifecycle_state == "new":
                msg = _("Nouveauté.")

            if rec.lifecycle_support_end and rec.lifecycle_support_end <= today:
                msg = _("Certification / support expiré depuis le %s.",
                        rec.lifecycle_support_end.strftime("%d/%m/%Y"))

            if rec.lifecycle_replacement_id and rec.lifecycle_state in ("eol_soon", "eol", "obsolete"):
                msg += _(" Remplacé par %s.", rec.lifecycle_replacement_id.name)

            rec.lifecycle_warning = msg
