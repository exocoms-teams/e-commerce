from odoo import api, fields, models


class AutoSpecification(models.Model):
    _name = "auto.specification"
    _description = "Spécification du véhicule"
    _order = "sequence, id"

    SECTION_SELECTION = [
        ("performance", "Performance"),
        ("dimensions", "Dimensions"),
        ("energy", "Énergie"),
        ("safety", "Sécurité"),
        ("comfort", "Confort"),
        ("other", "Autre"),
    ]

    vehicle_id = fields.Many2one("auto.vehicle", required=True, ondelete="cascade")
    sequence = fields.Integer(default=10)
    section = fields.Selection(SECTION_SELECTION, default="other", required=True)
    section_label = fields.Char(compute="_compute_section_label")
    name = fields.Char(required=True, translate=True)
    value = fields.Char(required=True, translate=True)
    unit = fields.Char(translate=True)

    @api.depends("section")
    @api.depends_context("lang")
    def _compute_section_label(self):
        labels = dict(self._fields["section"]._description_selection(self.env))
        for specification in self:
            specification.section_label = labels.get(specification.section)
