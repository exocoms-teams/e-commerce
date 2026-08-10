# -*- coding: utf-8 -*-
import logging
from odoo import _, api, fields, models

_logger = logging.getLogger(__name__)


class ProductSpecAutoFetch(models.Model):
    """
    Récupération automatique planifiée des caractéristiques manquantes.
    Traite les produits incomplets par lots, avec journal d'exécution.
    """
    _name        = "product.spec.autofetch.run"
    _description = "Exécution de récupération automatique"
    _inherit     = ["mail.thread"]
    _order       = "create_date desc"

    name           = fields.Char(string="Exécution", readonly=True)
    date_start     = fields.Datetime(string="Début", readonly=True)
    date_end       = fields.Datetime(string="Fin", readonly=True)
    product_count  = fields.Integer(string="Produits traités", readonly=True)
    success_count  = fields.Integer(string="Réussites", readonly=True)
    failed_count   = fields.Integer(string="Échecs", readonly=True)
    lines_created  = fields.Integer(string="Caractéristiques créées", readonly=True)
    state          = fields.Selection(
        [("running", "En cours"), ("done", "Terminée"), ("error", "Erreur")],
        default="running", readonly=True,
    )
    log = fields.Text(string="Journal", readonly=True)

    # ── Point d'entrée du cron ────────────────────────────────────
    @api.model
    def cron_fetch_missing_specs(self, batch_size=None):
        """
        Action planifiée : complète les fiches produit incomplètes.
        Le nombre de produits par exécution est réglable dans les paramètres.
        """
        ICP = self.env["ir.config_parameter"].sudo()

        if not ICP.get_param("product_spec_sheet.autofetch_enabled", default="False") == "True":
            _logger.info("Récupération automatique désactivée — cron ignoré.")
            return False

        if batch_size is None:
            batch_size = int(ICP.get_param("product_spec_sheet.autofetch_batch", default="20"))

        # Produits à compléter : publiés, vendables, fiche incomplète
        domain = [
            ("sale_ok", "=", True),
            ("spec_quality_level", "!=", "complete"),
        ]
        if ICP.get_param("product_spec_sheet.autofetch_published_only", default="True") == "True":
            domain.append(("website_published", "=", True))

        products = self.env["product.template"].search(
            domain, limit=batch_size, order="spec_completeness asc, write_date asc"
        )

        run = self.create({
            "name":       _("Récupération du %s") % fields.Datetime.now().strftime("%d/%m/%Y %H:%M"),
            "date_start": fields.Datetime.now(),
            "state":      "running",
        })

        if not products:
            run.write({
                "date_end": fields.Datetime.now(),
                "state":    "done",
                "log":      _("Aucun produit à compléter."),
            })
            return True

        api_key = ICP.get_param("product_spec_sheet.anthropic_api_key", default="")
        Wizard  = self.env["product.spec.fetch.wizard"]

        success = failed = created_total = 0
        logs = []

        for product in products:
            try:
                wizard = Wizard.create({
                    "product_tmpl_id":     product.id,
                    "product_search_name": product.name,
                    "apply_weight":        True,
                    "apply_spec_lines":    True,
                    "update_existing":     False,   # ne pas écraser le travail manuel
                })
                result = wizard._do_fetch(product.name, api_key)

                if not result or not (result.get("weight_kg") or result.get("os")):
                    failed += 1
                    logs.append(_("[ÉCHEC] %s — aucune donnée trouvée") % product.name)
                    continue

                wizard._fill_from_result(result)
                before = len(product.spec_line_ids)
                wizard.with_context(spec_change_source="cron").action_apply()
                after = len(product.spec_line_ids)

                created_total += (after - before)
                success += 1
                logs.append(_("[OK] %(p)s — %(n)d ligne(s), confiance %(c)s") % {
                    "p": product.name,
                    "n": after - before,
                    "c": result.get("confidence", "?"),
                })

                self.env.cr.commit()

            except Exception as e:
                failed += 1
                logs.append(_("[ERREUR] %(p)s — %(e)s") % {"p": product.name, "e": str(e)[:120]})
                _logger.warning("Autofetch échec sur %s : %s", product.name, e)

        run.write({
            "date_end":      fields.Datetime.now(),
            "product_count": len(products),
            "success_count": success,
            "failed_count":  failed,
            "lines_created": created_total,
            "state":         "done" if success else "error",
            "log":           "\n".join(logs),
        })

        # Notification aux managers si configuré
        notify_uid = ICP.get_param("product_spec_sheet.autofetch_notify_uid")
        if notify_uid and str(notify_uid).isdigit():
            user = self.env["res.users"].browse(int(notify_uid))
            if user.exists() and user.partner_id:
                run.message_notify(
                    partner_ids=user.partner_id.ids,
                    subject=_("Récupération automatique des caractéristiques"),
                    body=_(
                        "<p>%(s)d produit(s) complété(s), %(f)d échec(s).<br/>"
                        "%(l)d caractéristique(s) ajoutée(s).</p>",
                        s=success, f=failed, l=created_total,
                    ),
                )

        _logger.info(
            "Autofetch terminé : %d OK, %d échecs, %d lignes créées.",
            success, failed, created_total,
        )
        return True

    def action_run_now(self):
        """Lance une exécution manuelle depuis l'interface."""
        self.env["product.spec.autofetch.run"].cron_fetch_missing_specs()
        return {
            "type": "ir.actions.client",
            "tag":  "reload",
        }
