from odoo import _, api, fields, models


class AutoQuoteRequest(models.Model):
    _name = "auto.quote.request"
    _description = "Demande de devis véhicule"
    _inherit = ["mail.thread", "mail.activity.mixin"]
    _order = "id desc"

    STATE_SELECTION = [
        ("new", "Nouvelle"),
        ("qualified", "Qualifiée"),
        ("quoted", "Devis envoyé"),
        ("won", "Gagnée"),
        ("lost", "Perdue"),
    ]

    name = fields.Char(default="Nouveau", readonly=True, copy=False)
    partner_id = fields.Many2one("res.partner", required=True, tracking=True)
    vehicle_id = fields.Many2one("auto.vehicle", required=True, tracking=True)
    email = fields.Char(required=True)
    phone = fields.Char()
    budget = fields.Monetary(currency_field="currency_id")
    message = fields.Text()
    preferred_contact = fields.Selection(
        [("email", "Email"), ("phone", "Téléphone"), ("whatsapp", "WhatsApp")],
        default="email",
    )
    source = fields.Char(default="website")
    state = fields.Selection(STATE_SELECTION, default="new", tracking=True)
    lead_id = fields.Many2one("crm.lead", readonly=True)
    sale_order_id = fields.Many2one("sale.order", readonly=True)
    assigned_user_id = fields.Many2one("res.users", string="Conseiller assigné", tracking=True)
    company_id = fields.Many2one("res.company", default=lambda self: self.env.company)
    currency_id = fields.Many2one("res.currency", related="company_id.currency_id", readonly=True)

    @api.model_create_multi
    def create(self, vals_list):
        seq = self.env["ir.sequence"]
        for vals in vals_list:
            if vals.get("name", "Nouveau") in ("New", "Nouveau"):
                vals["name"] = seq.next_by_code("auto.quote.request") or "Nouveau"
        requests = super().create(vals_list)
        template = self.env.ref("auto_sale.mail_template_quote_request_received", raise_if_not_found=False)
        for quote in requests:
            if template and quote.email:
                template.send_mail(quote.id, force_send=True)
        return requests

    def action_set_qualified(self):
        self.write({"state": "qualified"})

    def action_set_quoted(self):
        self.write({"state": "quoted"})

    def action_set_won(self):
        self.write({"state": "won"})

    def action_set_lost(self):
        self.write({"state": "lost"})

    def action_create_lead(self):
        crm_lead_model = self.env["crm.lead"]
        for quote in self:
            if quote.lead_id:
                continue
            lead = crm_lead_model.create(
                {
                    "name": _("Demande de devis: %s") % quote.vehicle_id.display_name,
                    "partner_id": quote.partner_id.id,
                    "email_from": quote.email,
                    "phone": quote.phone,
                    "description": quote.message or "",
                    "user_id": quote.assigned_user_id.id or False,
                    "type": "opportunity",
                }
            )
            quote.lead_id = lead.id
        return True

    def action_create_sale_order(self):
        sale_order_model = self.env["sale.order"]
        for quote in self:
            if quote.sale_order_id:
                continue
            product = quote.vehicle_id.product_template_id.product_variant_id
            order = sale_order_model.create(
                {
                    "partner_id": quote.partner_id.id,
                    "origin": quote.name,
                    "order_line": [
                        (
                            0,
                            0,
                            {
                                "product_id": product.id,
                                "name": quote.vehicle_id.display_name,
                                "product_uom_qty": 1,
                                "price_unit": quote.vehicle_id.list_price,
                                "auto_vehicle_id": quote.vehicle_id.id,
                            },
                        )
                    ],
                }
            )
            quote.sale_order_id = order.id
            quote.state = "quoted"
        return True
