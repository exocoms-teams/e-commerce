# -*- coding: utf-8 -*-
from odoo import _, api, fields, models


class ProductTemplateSpecLine(models.Model):
    """Valeur d'une caractéristique pour un produit donné, avec historique."""

    _name = 'product.template.spec.line'
    _description = "Ligne de caractéristique produit"
    _order = 'category_id, sequence, id'

    product_tmpl_id = fields.Many2one(
        'product.template', string="Produit",
        required=True, ondelete='cascade', index=True,
    )
    attribute_id = fields.Many2one(
        'product.spec.attribute', string="Caractéristique",
        required=True, ondelete='restrict',
    )
    category_id = fields.Many2one(
        related='attribute_id.category_id', store=True, readonly=True,
        string="Catégorie",
    )
    sequence = fields.Integer(related='attribute_id.sequence', store=True, readonly=True)
    value = fields.Char(string="Valeur", required=True, translate=True)

    # ── Traçabilité ───────────────────────────────────────────────
    last_change_date = fields.Datetime(
        string="Dernière modification", readonly=True,
    )
    last_change_uid = fields.Many2one(
        'res.users', string="Modifié par", readonly=True,
    )
    previous_value = fields.Char(
        string="Valeur précédente", readonly=True,
    )
    change_source = fields.Selection(
        [
            ("manual",  "Saisie manuelle"),
            ("import",  "Import en masse"),
            ("fetch",   "Récupération internet"),
            ("cron",    "Récupération automatique"),
        ],
        string="Origine", default="manual", readonly=True,
    )

    _uniq_attribute_per_product = models.Constraint(
        'unique(product_tmpl_id, attribute_id)',
        "Cette caractéristique est déjà renseignée pour ce produit.",
    )

    @api.model_create_multi
    def create(self, vals_list):
        source = self.env.context.get("spec_change_source", "manual")
        now = fields.Datetime.now()
        for vals in vals_list:
            vals.setdefault("change_source", source)
            vals["last_change_date"] = now
            vals["last_change_uid"] = self.env.uid
        lines = super().create(vals_list)
        for line in lines:
            line.product_tmpl_id.message_post(body=_(
                "Caractéristique ajoutée — <b>%(a)s</b> : %(v)s",
                a=line.attribute_id.name, v=line.value,
            ))
        return lines

    def write(self, vals):
        if "value" in vals:
            source = self.env.context.get("spec_change_source", "manual")
            now = fields.Datetime.now()
            for line in self:
                old = line.value
                new = vals["value"]
                if old == new:
                    continue
                super(ProductTemplateSpecLine, line).write({
                    **vals,
                    "previous_value":   old,
                    "last_change_date": now,
                    "last_change_uid":  self.env.uid,
                    "change_source":    source,
                })
                line.product_tmpl_id.message_post(body=_(
                    "Caractéristique modifiée — <b>%(a)s</b> : "
                    "<span style='text-decoration:line-through;color:#888'>%(o)s</span> "
                    "&rarr; %(n)s",
                    a=line.attribute_id.name, o=old, n=new,
                ))
            return True
        return super().write(vals)

    def unlink(self):
        for line in self:
            line.product_tmpl_id.message_post(body=_(
                "Caractéristique supprimée — <b>%(a)s</b> (valeur : %(v)s)",
                a=line.attribute_id.name, v=line.value,
            ))
        return super().unlink()
