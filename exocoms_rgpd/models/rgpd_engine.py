# -*- coding: utf-8 -*-
"""Moteur RGPD : collecte, anonymisation et pseudonymisation des données.

Ce modèle abstrait centralise toute la logique manipulant réellement les
données personnelles. Les demandes de droits, les règles de conservation et
les assistants s'appuient dessus afin qu'il n'existe qu'une seule
implémentation de l'anonymisation dans le module.
"""

import hashlib
import logging
import uuid
from datetime import date, datetime

from odoo import _, api, fields, models
from odoo.exceptions import UserError
from odoo.tools.safe_eval import safe_eval

_logger = logging.getLogger(__name__)

ANONYMOUS_LABEL = "Anonymisé"

STRATEGIES = [
    ("clear", "Vider la valeur"),
    ("fixed", "Valeur fixe"),
    ("hash", "Hachage SHA-256 (pseudonymisation)"),
    ("mask_email", "Masquer l'e-mail"),
    ("mask_phone", "Masquer le téléphone"),
    ("mask_name", "Remplacer par « Anonymisé »"),
    ("mask_address", "Masquer l'adresse"),
    ("date_year", "Ne conserver que l'année"),
    ("keep", "Conserver (obligation légale)"),
]


class RgpdEngine(models.AbstractModel):
    _name = "exocoms.rgpd.engine"
    _description = "RGPD - Moteur de collecte et d'anonymisation"

    # ------------------------------------------------------------------
    # Utilitaires de transformation
    # ------------------------------------------------------------------
    @api.model
    def _hash_value(self, value, salt=None):
        """Pseudonymisation irréversible d'une valeur."""
        if value in (False, None, ""):
            return False
        salt = salt or self.env["ir.config_parameter"].sudo().get_param(
            "exocoms_rgpd.hash_salt", ""
        )
        raw = "%s%s" % (salt, value)
        return hashlib.sha256(raw.encode("utf-8")).hexdigest()[:32]

    @api.model
    def _anonymize_value(self, field, value, strategy, fixed_value=None):
        """Retourne la nouvelle valeur d'un champ selon la stratégie choisie."""
        ttype = field.type
        if strategy == "keep":
            return None  # signal : ne pas écrire
        if strategy == "fixed":
            return fixed_value if ttype in ("char", "text", "html") else False
        if strategy == "clear":
            if ttype in ("char", "text", "html"):
                return False
            if ttype in ("many2one", "date", "datetime"):
                return False
            if ttype in ("integer", "float", "monetary"):
                return 0
            if ttype == "boolean":
                return False
            if ttype in ("many2many", "one2many"):
                return [(5, 0, 0)]
            if ttype == "selection":
                return False
            if ttype == "binary":
                return False
            return False
        if strategy == "hash":
            return self._hash_value(value)
        if strategy == "mask_email":
            return "anonyme+%s@invalid.local" % uuid.uuid4().hex[:10]
        if strategy == "mask_phone":
            return "+00000000000"
        if strategy == "mask_name":
            return ANONYMOUS_LABEL
        if strategy == "mask_address":
            return ANONYMOUS_LABEL
        if strategy == "date_year":
            if isinstance(value, (date, datetime)):
                return value.replace(month=1, day=1)
            return False
        return False

    # ------------------------------------------------------------------
    # Résolution des enregistrements liés à une personne
    # ------------------------------------------------------------------
    @api.model
    def _partner_domain(self, data_map, partner):
        """Construit le domaine permettant de retrouver les enregistrements
        d'un modèle rattachés à une personne concernée."""
        domain = []
        link = data_map.link_type
        if link == "partner" and data_map.partner_field_name:
            domain = [(data_map.partner_field_name, "=", partner.id)]
        elif link == "email" and data_map.partner_field_name:
            if not partner.email:
                return None
            domain = [(data_map.partner_field_name, "=ilike", partner.email)]
        elif link == "self":
            domain = [("id", "=", partner.id)]
        else:
            return None
        if data_map.extra_domain:
            domain += safe_eval(data_map.extra_domain)
        return domain

    @api.model
    def _get_related_records(self, data_map, partner):
        model = self.env.get(data_map.model_name)
        if model is None:
            return None
        domain = self._partner_domain(data_map, partner)
        if domain is None:
            return None
        try:
            return model.sudo().with_context(active_test=False).search(domain)
        except Exception as exc:  # pragma: no cover - modèle exotique
            _logger.warning(
                "RGPD: recherche impossible sur %s (%s)", data_map.model_name, exc
            )
            return None

    # ------------------------------------------------------------------
    # Collecte (droit d'accès et portabilité)
    # ------------------------------------------------------------------
    @api.model
    def collect_personal_data(self, partner):
        """Retourne un dictionnaire structuré de toutes les données
        personnelles connues pour ``partner``."""
        partner = partner.sudo()
        maps = (
            self.env["exocoms.rgpd.data.map"]
            .sudo()
            .search([("include_in_export", "=", True)], order="sequence, id")
        )
        result = {
            "meta": {
                "generated_at": fields.Datetime.now().isoformat(),
                "controller": self.env.company.name,
                "controller_vat": self.env.company.vat or "",
                "subject": {
                    "id": partner.id,
                    "name": partner.name,
                    "email": partner.email or "",
                },
                "format": "EXOCOMS-RGPD/1.0",
                "notice": "Export réalisé au titre des articles 15 et 20 du RGPD.",
            },
            "sections": [],
        }
        for dmap in maps:
            records = self._get_related_records(dmap, partner)
            if records is None or not records:
                continue
            field_names = [f.field_name for f in dmap.field_ids if f.field_name]
            if not field_names:
                field_names = self._default_export_fields(dmap.model_name)
            model = self.env[dmap.model_name].sudo()
            available = [f for f in field_names if f in model._fields]
            rows = []
            for rec in records[: dmap.export_limit or 500]:
                row = {}
                for fname in available:
                    field = model._fields[fname]
                    value = rec[fname]
                    row[field.string or fname] = self._serialize(field, value)
                rows.append(row)
            if rows:
                result["sections"].append(
                    {
                        "model": dmap.model_name,
                        "title": dmap.name or model._description,
                        "category": dmap.category_id.name or "",
                        "count": len(records),
                        "truncated": len(records) > len(rows),
                        "records": rows,
                    }
                )
        return result

    @api.model
    def _default_export_fields(self, model_name):
        model = self.env.get(model_name)
        if model is None:
            return []
        skip = {"id", "create_uid", "write_uid", "__last_update", "display_name"}
        names = []
        for name, field in model._fields.items():
            if name in skip or field.type in ("one2many", "many2many", "binary"):
                continue
            if field.compute and not field.store:
                continue
            names.append(name)
        return names[:40]

    @api.model
    def _serialize(self, field, value):
        if value is False or value is None:
            return ""
        if field.type == "many2one":
            return value.display_name
        if field.type in ("many2many", "one2many"):
            return ", ".join(value.mapped("display_name"))
        if field.type in ("date", "datetime"):
            return fields.Date.to_string(value) if field.type == "date" else fields.Datetime.to_string(value)
        if field.type == "selection":
            selection = dict(field._description_selection(self.env))
            return selection.get(value, value)
        if field.type == "binary":
            return "[fichier binaire]"
        return value

    # ------------------------------------------------------------------
    # Effacement / anonymisation (art. 17)
    # ------------------------------------------------------------------
    @api.model
    def anonymize_partner(self, partner, dry_run=True, reason=None):
        """Anonymise l'ensemble des enregistrements liés à ``partner``.

        Retourne un rapport détaillé. Avec ``dry_run=True`` aucune écriture
        n'est effectuée : la méthode sert alors de simulation.
        """
        partner = partner.sudo()
        maps = (
            self.env["exocoms.rgpd.data.map"]
            .sudo()
            .search([], order="sequence, id")
        )
        report = {
            "dry_run": dry_run,
            "partner": partner.display_name,
            "reason": reason or "",
            "processed": [],
            "blocked": [],
            "errors": [],
            "total": 0,
        }
        for dmap in maps:
            records = self._get_related_records(dmap, partner)
            if records is None or not records:
                continue
            if dmap.legal_hold:
                report["blocked"].append(
                    {
                        "model": dmap.model_name,
                        "title": dmap.name,
                        "count": len(records),
                        "reason": dmap.legal_hold_note
                        or _("Conservation imposée par une obligation légale."),
                    }
                )
                continue
            if not dmap.include_in_erasure:
                continue
            values = {}
            for fmap in dmap.field_ids:
                if fmap.strategy == "keep" or not fmap.field_name:
                    continue
                model = self.env[dmap.model_name]
                if fmap.field_name not in model._fields:
                    continue
                field = model._fields[fmap.field_name]
                if field.readonly and not field.inverse:
                    continue
                new_value = self._anonymize_value(
                    field, None, fmap.strategy, fmap.fixed_value
                )
                if new_value is None:
                    continue
                values[fmap.field_name] = new_value
            if not values:
                continue
            report["total"] += len(records)
            report["processed"].append(
                {
                    "model": dmap.model_name,
                    "title": dmap.name,
                    "count": len(records),
                    "fields": sorted(values.keys()),
                }
            )
            if dry_run:
                continue
            for rec in records:
                try:
                    payload = dict(values)
                    for fname, strategy in [
                        (f.field_name, f.strategy) for f in dmap.field_ids
                    ]:
                        if strategy in ("hash", "date_year") and fname in payload:
                            field = rec._fields[fname]
                            payload[fname] = self._anonymize_value(
                                field, rec[fname], strategy
                            )
                    rec.with_context(rgpd_anonymizing=True,mail_notrack=True).write(payload)
                except Exception as exc:
                    _logger.exception("RGPD: anonymisation impossible")
                    report["errors"].append(
                        {"model": dmap.model_name, "id": rec.id, "error": str(exc)}
                    )
        if not dry_run:
            partner.with_context(rgpd_anonymizing=True,mail_notrack=True).write(
                {"rgpd_anonymized": True, "rgpd_anonymized_date": fields.Datetime.now()}
            )
        return report

    # ------------------------------------------------------------------
    # Anonymisation générique d'un jeu d'enregistrements (conservation)
    # ------------------------------------------------------------------
    @api.model
    def anonymize_records(self, records, field_maps, dry_run=True):
        """Applique une liste de stratégies à un recordset quelconque."""
        if not records:
            return 0
        model = records._name
        applicable = []
        for fmap in field_maps:
            if fmap.strategy == "keep" or not fmap.field_name:
                continue
            if fmap.field_name not in records._fields:
                continue
            applicable.append(fmap)
        if not applicable:
            raise UserError(
                _("Aucun champ valide à anonymiser sur le modèle %s.") % model
            )
        if dry_run:
            return len(records)
        count = 0
        for rec in records:
            payload = {}
            for fmap in applicable:
                field = rec._fields[fmap.field_name]
                payload[fmap.field_name] = self._anonymize_value(
                    field, rec[fmap.field_name], fmap.strategy, fmap.fixed_value
                )
            payload = {k: v for k, v in payload.items() if v is not None}
            if payload:
                rec.with_context(rgpd_anonymizing=True,mail_notrack=True).write(payload)
                count += 1
        return count
