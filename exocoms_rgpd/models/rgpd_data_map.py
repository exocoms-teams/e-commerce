# -*- coding: utf-8 -*-
"""Cartographie des données personnelles dans la base Odoo."""

import logging

from odoo import _, api, fields, models
from odoo.exceptions import UserError

from .rgpd_engine import STRATEGIES

_logger = logging.getLogger(__name__)

# Modèles exclus de l'auto-détection : techniques, transitoires ou système.
EXCLUDED_PREFIXES = (
    "ir.", "base.", "bus.", "res.config", "report.", "mail.tracking",
    "mail.notification", "mail.followers", "web_", "wizard.", "iap.",
    "exocoms.rgpd.",
)

PARTNER_FIELD_CANDIDATES = (
    "partner_id", "customer_id", "supplier_id", "commercial_partner_id",
    "contact_id", "member_id", "employee_partner_id", "recipient_id",
)
EMAIL_FIELD_CANDIDATES = ("email", "email_from", "partner_email", "contact_email")


class RgpdDataMap(models.Model):
    _name = "exocoms.rgpd.data.map"
    _description = "RGPD - Cartographie des données personnelles"
    _order = "sequence, id"

    name = fields.Char(string="Libellé", required=True)
    sequence = fields.Integer(default=10)
    active = fields.Boolean(default=True)
    model_id = fields.Many2one(
        "ir.model", string="Modèle", required=True, ondelete="cascade",
        domain=[("transient", "=", False)],
    )
    model_name = fields.Char(related="model_id.model", store=True, string="Modèle technique")
    category_id = fields.Many2one(
        "exocoms.rgpd.data.category", string="Catégorie de données"
    )
    treatment_ids = fields.Many2many(
        "exocoms.rgpd.treatment", string="Traitements concernés"
    )

    link_type = fields.Selection(
        [
            ("self", "L'enregistrement est la personne (res.partner)"),
            ("partner", "Champ relationnel vers res.partner"),
            ("email", "Champ e-mail (rapprochement textuel)"),
        ],
        string="Type de rattachement", required=True, default="partner",
    )
    partner_field_id = fields.Many2one(
        "ir.model.fields", string="Champ de rattachement",
        domain="[('model_id', '=', model_id), ('ttype', 'in', ['many2one', 'char'])]",
        ondelete="cascade",
    )
    partner_field_name = fields.Char(
        related="partner_field_id.name", store=True, string="Champ technique"
    )
    extra_domain = fields.Char(
        string="Domaine complémentaire", default="[]",
        help="Domaine Odoo appliqué en plus du rattachement, ex. [('state','!=','cancel')]",
    )

    include_in_export = fields.Boolean(
        string="Inclure dans l'export", default=True,
        help="Les enregistrements sont repris dans la réponse au droit d'accès "
        "et de portabilité.",
    )
    export_limit = fields.Integer(
        string="Limite d'export", default=500,
        help="Nombre maximal d'enregistrements repris par section dans l'export.",
    )
    include_in_erasure = fields.Boolean(
        string="Inclure dans l'effacement", default=True
    )
    legal_hold = fields.Boolean(
        string="Conservation obligatoire",
        help="Les données ne peuvent pas être effacées : obligation légale de "
        "conservation (comptabilité, paie, garantie décennale...).",
    )
    legal_hold_note = fields.Char(string="Fondement de la conservation")
    field_ids = fields.One2many(
        "exocoms.rgpd.data.map.field", "map_id", string="Champs personnels"
    )
    field_count = fields.Integer(compute="_compute_field_count")
    note = fields.Text(string="Notes")

    _rgpd_map_model_uniq = models.Constraint(
        "unique(model_id, partner_field_id)",
        "Cette combinaison modèle / champ de rattachement existe déjà.",
    )

    @api.depends("field_ids")
    def _compute_field_count(self):
        for rec in self:
            rec.field_count = len(rec.field_ids)

    @api.onchange("model_id")
    def _onchange_model_id(self):
        self.partner_field_id = False
        if not self.model_id:
            return
        if self.model_id.model == "res.partner":
            self.link_type = "self"
            self.name = self.name or self.model_id.name
            return
        model = self.env.get(self.model_id.model)
        if model is None:
            return
        for candidate in PARTNER_FIELD_CANDIDATES:
            field = model._fields.get(candidate)
            if field is not None and field.type == "many2one" and field.comodel_name == "res.partner":
                self.link_type = "partner"
                self.partner_field_id = self.env["ir.model.fields"].search(
                    [("model", "=", self.model_id.model), ("name", "=", candidate)], limit=1
                )
                break
        self.name = self.name or self.model_id.name

    @api.constrains("link_type", "partner_field_id")
    def _check_link(self):
        for rec in self:
            if rec.link_type in ("partner", "email") and not rec.partner_field_id:
                raise UserError(
                    _("Le champ de rattachement est obligatoire pour ce type de lien.")
                )

    # ------------------------------------------------------------------
    # Auto-détection
    # ------------------------------------------------------------------
    @api.model
    def action_autodetect(self):
        """Parcourt les modèles installés et crée les cartographies manquantes."""
        created = 0
        IrModelFields = self.env["ir.model.fields"]
        existing = set(self.with_context(active_test=False).search([]).mapped("model_name"))
        models_to_scan = self.env["ir.model"].search(
            [("transient", "=", False), ("model", "not in", list(existing))]
        )
        for imodel in models_to_scan:
            mname = imodel.model
            if mname.startswith(EXCLUDED_PREFIXES):
                continue
            model = self.env.get(mname)
            if model is None or not model._auto or model._abstract:
                continue
            if not self.env["ir.model.access"].check(mname, "read", raise_exception=False):
                continue
            link_type = partner_field = None
            for candidate in PARTNER_FIELD_CANDIDATES:
                field = model._fields.get(candidate)
                if field is not None and field.type == "many2one" and field.comodel_name == "res.partner":
                    link_type, partner_field = "partner", candidate
                    break
            if not link_type:
                for candidate in EMAIL_FIELD_CANDIDATES:
                    field = model._fields.get(candidate)
                    if field is not None and field.type == "char":
                        link_type, partner_field = "email", candidate
                        break
            if not link_type:
                continue
            field_rec = IrModelFields.search(
                [("model", "=", mname), ("name", "=", partner_field)], limit=1
            )
            if not field_rec:
                continue
            dmap = self.create(
                {
                    "name": imodel.name,
                    "model_id": imodel.id,
                    "link_type": link_type,
                    "partner_field_id": field_rec.id,
                    "include_in_export": True,
                    "include_in_erasure": False,
                }
            )
            dmap._populate_default_fields()
            created += 1
        return {
            "type": "ir.actions.client",
            "tag": "display_notification",
            "params": {
                "title": _("Auto-détection terminée"),
                "message": _("%s modèle(s) contenant des données personnelles "
                             "ont été ajoutés à la cartographie.") % created,
                "type": "success",
                "next": {"type": "ir.actions.act_window_close"},
            },
        }

    def action_populate_fields(self):
        for rec in self:
            rec._populate_default_fields()

    def _populate_default_fields(self):
        """Pré-remplit la liste des champs personnels avec une stratégie."""
        self.ensure_one()
        model = self.env.get(self.model_name)
        if model is None:
            return
        known = set(self.field_ids.mapped("field_name"))
        heuristics = [
            (("name", "display_name", "contact_name", "partner_name", "firstname", "lastname"), "mask_name"),
            (("email", "email_from", "partner_email", "contact_email"), "mask_email"),
            (("phone", "mobile", "fax", "partner_phone"), "mask_phone"),
            (("street", "street2", "zip", "city", "address"), "mask_address"),
            (("vat", "siret", "ref", "barcode", "login"), "hash"),
            (("comment", "description", "note", "x_note"), "clear"),
            (("birthday", "birthdate", "date_of_birth"), "date_year"),
        ]
        vals = []
        IrModelFields = self.env["ir.model.fields"]
        for names, strategy in heuristics:
            for fname in names:
                if fname in known:
                    continue
                field = model._fields.get(fname)
                if field is None or field.type in ("one2many", "many2many"):
                    continue
                if field.compute and not field.store:
                    continue
                frec = IrModelFields.search(
                    [("model", "=", self.model_name), ("name", "=", fname)], limit=1
                )
                if not frec:
                    continue
                vals.append(
                    (0, 0, {"field_id": frec.id, "strategy": strategy})
                )
                known.add(fname)
        if vals:
            self.write({"field_ids": vals})

    def action_open_records(self):
        self.ensure_one()
        return {
            "type": "ir.actions.act_window",
            "name": self.name,
            "res_model": self.model_name,
            "view_mode": "list,form",
        }


class RgpdDataMapField(models.Model):
    _name = "exocoms.rgpd.data.map.field"
    _description = "RGPD - Champ personnel cartographié"
    _order = "map_id, sequence, id"

    map_id = fields.Many2one(
        "exocoms.rgpd.data.map", string="Cartographie", required=True, ondelete="cascade"
    )
    sequence = fields.Integer(default=10)
    model_name = fields.Char(related="map_id.model_name", store=True)
    field_id = fields.Many2one(
        "ir.model.fields", string="Champ", required=True, ondelete="cascade",
        domain="[('model', '=', model_name)]",
    )
    field_name = fields.Char(related="field_id.name", store=True, string="Nom technique")
    field_label = fields.Char(related="field_id.field_description", string="Libellé")
    strategy = fields.Selection(
        STRATEGIES, string="Stratégie d'anonymisation", required=True, default="clear"
    )
    fixed_value = fields.Char(string="Valeur fixe")
    sensitive = fields.Boolean(string="Donnée sensible")

    _rgpd_map_field_uniq = models.Constraint(
        "unique(map_id, field_id)",
        "Ce champ est déjà cartographié pour ce modèle.",
    )
