# -*- coding: utf-8 -*-
import base64
from odoo import _, api, fields, models
from odoo.exceptions import UserError


class SaleOrder(models.Model):
    _inherit = "sale.order"

    spec_product_count = fields.Integer(
        string="Produits avec fiche technique",
        compute="_compute_spec_product_count",
    )

    @api.depends("order_line.product_id")
    def _compute_spec_product_count(self):
        for order in self:
            products = order.order_line.mapped("product_id.product_tmpl_id")
            order.spec_product_count = len(
                products.filtered(lambda p: p.spec_line_ids)
            )

    def _get_spec_products(self):
        """Produits de la commande qui ont des caractéristiques renseignées."""
        self.ensure_one()
        products = self.order_line.filtered(
            lambda l: not l.display_type and l.product_id
        ).mapped("product_id.product_tmpl_id")
        # Déduplique en conservant l'ordre des lignes
        seen, ordered = set(), self.env["product.template"]
        for p in products:
            if p.id not in seen and p.spec_line_ids:
                seen.add(p.id)
                ordered |= p
        return ordered

    def action_attach_spec_sheets(self):
        """
        Génère un PDF regroupant les fiches techniques de tous les produits
        de la commande et l'attache au devis.
        """
        self.ensure_one()
        products = self._get_spec_products()

        if not products:
            raise UserError(_(
                "Aucun produit de ce devis n'a de caractéristiques renseignées.\n\n"
                "Complétez les fiches depuis Ventes > Configuration > Qualité des fiches."
            ))

        report_ref = "product_spec_sheet.report_product_spec_sheet_single"
        pdf_content, _ctype = self.env["ir.actions.report"].sudo()._render_qweb_pdf(
            report_ref, res_ids=products.ids
        )

        filename = _("Fiches techniques - %s.pdf") % (self.name or "Devis")
        attachment = self.env["ir.attachment"].create({
            "name":      filename,
            "type":      "binary",
            "datas":     base64.b64encode(pdf_content),
            "res_model": self._name,
            "res_id":    self.id,
            "mimetype":  "application/pdf",
        })

        self.message_post(
            body=_(
                "Fiches techniques générées pour %(n)d produit(s) : %(p)s",
                n=len(products),
                p=", ".join(products.mapped("name")[:5]),
            ),
            attachment_ids=[attachment.id],
        )

        return {
            "type": "ir.actions.client",
            "tag":  "display_notification",
            "params": {
                "title":   _("Fiches techniques jointes"),
                "message": _(
                    "%(n)d fiche(s) technique(s) ajoutée(s) en pièce jointe du devis.",
                    n=len(products),
                ),
                "type":   "success",
                "sticky": False,
            },
        }

    def action_print_spec_sheets(self):
        """Imprime directement le PDF groupé sans l'attacher."""
        self.ensure_one()
        products = self._get_spec_products()
        if not products:
            raise UserError(_("Aucun produit de ce devis n'a de caractéristiques renseignées."))
        return self.env.ref(
            "product_spec_sheet.action_report_product_spec_sheet_single"
        ).report_action(products)

    def action_print_spec_comparison(self):
        """Imprime un comparatif des produits du devis."""
        self.ensure_one()
        products = self._get_spec_products()
        if len(products) < 2:
            raise UserError(_(
                "Le comparatif nécessite au moins deux produits avec des caractéristiques."
            ))
        return self.env.ref(
            "product_spec_sheet.action_report_product_spec_compare"
        ).report_action(products)
