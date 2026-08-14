# -*- coding: utf-8 -*-
from odoo import api, fields, models


class RgpdRecipient(models.Model):
    """Destinataires et sous-traitants (art. 28 et 30.1.d)."""

    _name = "exocoms.rgpd.recipient"
    _description = "RGPD - Destinataire / Sous-traitant"
    _order = "name"

    name = fields.Char(string="Destinataire", required=True)
    partner_id = fields.Many2one("res.partner", string="Contact lié")
    recipient_type = fields.Selection(
        [
            ("internal", "Service interne"),
            ("processor", "Sous-traitant (art. 28)"),
            ("controller", "Responsable conjoint"),
            ("third_party", "Tiers"),
            ("authority", "Autorité / organisme public"),
        ],
        string="Type",
        required=True,
        default="processor",
    )
    country_id = fields.Many2one("res.country", string="Pays d'établissement")
    outside_eu = fields.Boolean(
        string="Hors UE/EEE",
        compute="_compute_outside_eu",
        store=True,
        readonly=False,
    )
    safeguard = fields.Selection(
        [
            ("adequacy", "Décision d'adéquation"),
            ("scc", "Clauses contractuelles types (CCT/SCC)"),
            ("bcr", "Règles d'entreprise contraignantes (BCR)"),
            ("derogation", "Dérogation (art. 49)"),
            ("none", "Aucune garantie"),
        ],
        string="Garantie du transfert",
    )
    dpa_signed = fields.Boolean(string="Contrat de sous-traitance signé (DPA)")
    dpa_date = fields.Date(string="Date du DPA")
    dpa_url = fields.Char(string="URL du DPA")
    purpose = fields.Text(string="Objet de la communication")
    note = fields.Text(string="Notes")
    active = fields.Boolean(default=True)
    company_id = fields.Many2one(
        "res.company", string="Société",
        help="Laissez vide pour un destinataire partagé par toutes les "
        "sociétés. Renseignez une société lorsque le contrat de sous-traitance "
        "est signé par une entité en particulier.",
    )

    @api.depends("country_id")
    def _compute_outside_eu(self):
        europe = self.env.ref("base.europe", raise_if_not_found=False)
        eu_countries = europe.country_ids if europe else self.env["res.country"]
        for rec in self:
            rec.outside_eu = bool(rec.country_id) and rec.country_id not in eu_countries

    @api.depends("name", "recipient_type")
    def _compute_display_name(self):
        labels = dict(self._fields["recipient_type"]._description_selection(self.env))
        for rec in self:
            if rec.recipient_type:
                rec.display_name = "%s (%s)" % (rec.name, labels.get(rec.recipient_type))
            else:
                rec.display_name = rec.name or ""
