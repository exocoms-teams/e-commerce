# -*- coding: utf-8 -*-
import logging
from odoo import _, api, fields, models
from odoo.exceptions import UserError

_logger = logging.getLogger(__name__)

PROVIDER_URLS = {
    "colissimo":  "https://api.laposte.fr/colissimo/v2",
    "chronopost": "https://www.chronopost.fr/shipping-cxf/ShippingServiceWS",
    "dhl":        "https://api.dhl.com/ecs/pcs",
    "ups":        "https://onlinetools.ups.com/api",
    "gls":        "https://api.gls-group.eu",
    "custom":     "",
}

PROVIDER_SEL = [
    ("colissimo",  "Colissimo (La Poste)"),
    ("chronopost", "Chronopost"),
    ("dhl",        "DHL Express"),
    ("ups",        "UPS"),
    ("gls",        "GLS"),
    ("custom",     "Transporteur personnalisé"),
]


class ProductSpecCarrierCreateWizard(models.TransientModel):
    """
    Assistant 3 étapes pour créer un transporteur via :
      - une clé API (tarifs en temps réel), ou
      - une grille tarifaire saisie manuellement (paliers poids → prix).
    """
    _name        = "product.spec.carrier.create.wizard"
    _description = "Ajouter un transporteur"

    # ── Étape 1 : choix de la méthode ─────────────────────────────
    state  = fields.Selection(
        [("method", "Méthode"), ("config", "Configuration"), ("summary", "Récapitulatif")],
        default="method", required=True,
    )
    method = fields.Selection(
        [("api", "Connexion API"), ("manual", "Grille tarifaire manuelle")],
        string="Méthode de configuration", default="api", required=True,
    )

    # ── Informations communes ──────────────────────────────────────
    name               = fields.Char(string="Nom du transporteur", required=True)
    volumetric_divisor = fields.Integer(
        string="Diviseur volumétrique", default=5000,
        help="Standard route : 5000 · Standard aérien : 6000",
    )
    max_weight_kg      = fields.Float(string="Poids maximum (kg)", default=30.0)
    note               = fields.Char(string="Note / conditions")
    sequence           = fields.Integer(default=99)

    # ── Étape 2a : configuration API ──────────────────────────────
    api_provider    = fields.Selection(PROVIDER_SEL, string="Fournisseur API", default="custom")
    api_base_url    = fields.Char(string="URL de base API")
    api_account_no  = fields.Char(string="Numéro de compte")
    api_key         = fields.Char(string="Clé API / Client ID")
    api_secret      = fields.Char(string="Secret / Token")
    api_timeout     = fields.Integer(string="Timeout (s)", default=8)
    api_depot_code  = fields.Char(string="Code agence / dépôt")
    api_use_live    = fields.Boolean(string="Tarifs en temps réel", default=True)
    api_fallback    = fields.Boolean(string="Fallback grille statique", default=True)
    api_tested      = fields.Boolean(default=False, readonly=True)
    api_test_msg    = fields.Char(string="Résultat du test", readonly=True)
    api_test_ok     = fields.Boolean(default=False, readonly=True)

    # ── Étape 2b : zones manuelles ────────────────────────────────
    zone_ids = fields.One2many(
        "product.spec.carrier.create.wizard.zone", "wizard_id",
        string="Zones tarifaires",
    )

    # ── Récap lecture seule ────────────────────────────────────────
    summary_html = fields.Html(string="Récapitulatif", readonly=True, sanitize=False)

    # ── Onchange provider → URL ───────────────────────────────────
    @api.onchange("api_provider")
    def _onchange_provider(self):
        if self.api_provider:
            self.api_base_url = PROVIDER_URLS.get(self.api_provider, "")

    # ── Navigation entre étapes ───────────────────────────────────
    def action_next(self):
        self.ensure_one()
        if self.state == "method":
            if not self.name:
                raise UserError(_("Renseignez le nom du transporteur avant de continuer."))
            if self.method == "manual" and not self.zone_ids:
                # Créer une zone exemple pour guider l'utilisateur
                self.env["product.spec.carrier.create.wizard.zone"].create({
                    "wizard_id": self.id,
                    "name": "France",
                    "sequence": 10,
                })
            self.state = "config"

        elif self.state == "config":
            self._build_summary()
            self.state = "summary"

        return self._reopen()

    def action_back(self):
        self.ensure_one()
        if self.state == "config":
            self.state = "method"
        elif self.state == "summary":
            self.state = "config"
        return self._reopen()

    def _reopen(self):
        return {
            "type":      "ir.actions.act_window",
            "res_model": self._name,
            "res_id":    self.id,
            "view_mode": "form",
            "target":    "new",
            "context":   self.env.context,
        }

    # ── Test de connexion API ─────────────────────────────────────
    def action_test_api(self):
        self.ensure_one()
        if not self.api_provider:
            raise UserError(_("Sélectionnez un fournisseur API."))

        # Créer temporairement un carrier pour réutiliser la logique de test
        temp_carrier = self.env["product.spec.carrier"].new({
            "name":            self.name or "TEST",
            "api_provider":    self.api_provider,
            "api_base_url":    self.api_base_url,
            "api_key":         self.api_key,
            "api_secret":      self.api_secret,
            "api_account_no":  self.api_account_no,
            "api_depot_code":  self.api_depot_code,
            "api_timeout":     self.api_timeout or 8,
        })

        ok, message, _price = temp_carrier._call_api_test()
        self.api_tested  = True
        self.api_test_ok = ok
        self.api_test_msg = message

        return {
            "type":   "ir.actions.client",
            "tag":    "display_notification",
            "params": {
                "title":   _("Connexion réussie") if ok else _("Échec de connexion"),
                "message": message,
                "type":    "success" if ok else "danger",
                "sticky":  not ok,
            },
        }

    # ── Construction du récapitulatif ─────────────────────────────
    def _build_summary(self):
        rows = f"""
            <div class="o_field_html">
            <table class="table table-sm table-bordered">
            <tbody>
            <tr><td class="text-muted" style="width:35%">Nom</td>
                <td><strong>{self.name}</strong></td></tr>
            <tr><td class="text-muted">Méthode</td>
                <td><span class="badge bg-{"info" if self.method == "api" else "warning"}">
                {"Connexion API" if self.method == "api" else "Grille manuelle"}</span></td></tr>
            <tr><td class="text-muted">Diviseur volumétrique</td>
                <td>{self.volumetric_divisor}</td></tr>
            <tr><td class="text-muted">Poids maximum</td>
                <td>{self.max_weight_kg:.1f} kg</td></tr>"""

        if self.method == "api":
            status = (
                '<span class="badge bg-success">Testée ✓</span>' if self.api_test_ok
                else '<span class="badge bg-warning">Non testée</span>' if not self.api_tested
                else '<span class="badge bg-danger">Échec</span>'
            )
            rows += f"""
            <tr><td class="text-muted">Fournisseur</td><td>{dict(PROVIDER_SEL).get(self.api_provider, "—")}</td></tr>
            <tr><td class="text-muted">URL API</td><td style="font-size:11px;">{self.api_base_url or "—"}</td></tr>
            <tr><td class="text-muted">Connexion testée</td><td>{status}</td></tr>
            <tr><td class="text-muted">Tarifs live</td>
                <td>{"Activés" if self.api_use_live else "Désactivés"}</td></tr>"""
        else:
            zone_lines = "".join(
                f"<tr><td class='text-muted' style='padding-left:16px;'>{z.name}</td>"
                f"<td>{len(z.threshold_ids)} palier(s)</td></tr>"
                for z in self.zone_ids
            )
            rows += f"""
            <tr><td class="text-muted">Zones</td><td>{len(self.zone_ids)} zone(s)</td></tr>
            {zone_lines}"""

        rows += "</tbody></table></div>"
        self.summary_html = rows

    # ── Enregistrement final ───────────────────────────────────────
    def action_save(self):
        self.ensure_one()
        Carrier = self.env["product.spec.carrier"]
        Zone    = self.env["product.spec.carrier.zone"]
        Thresh  = self.env["product.spec.carrier.zone.threshold"]

        vals = {
            "name":               self.name,
            "sequence":           self.sequence,
            "volumetric_divisor": self.volumetric_divisor,
            "max_weight_kg":      self.max_weight_kg,
            "note":               self.note or "",
            "active":             True,
        }

        if self.method == "api":
            vals.update({
                "api_provider":   self.api_provider,
                "api_base_url":   self.api_base_url,
                "api_account_no": self.api_account_no,
                "api_key":        self.api_key,
                "api_secret":     self.api_secret,
                "api_timeout":    self.api_timeout or 8,
                "api_depot_code": self.api_depot_code,
                "api_use_live":   self.api_use_live,
                "api_fallback":   self.api_fallback,
                "api_last_status": "ok" if self.api_test_ok else "untested",
                "api_last_message": self.api_test_msg or "",
            })

        carrier = Carrier.create(vals)

        # Créer les zones et paliers pour grille manuelle
        if self.method == "manual":
            for wzone in self.zone_ids.sorted("sequence"):
                zone = Zone.create({
                    "carrier_id": carrier.id,
                    "name":       wzone.name,
                    "sequence":   wzone.sequence,
                })
                for thresh in wzone.threshold_ids.sorted("max_weight_g"):
                    Thresh.create({
                        "zone_id":      zone.id,
                        "max_weight_g": thresh.max_weight_g,
                        "price_eur":    thresh.price_eur,
                    })

        return {
            "type":      "ir.actions.act_window",
            "res_model": "product.spec.carrier",
            "res_id":    carrier.id,
            "view_mode": "form",
            "target":    "current",
        }


class ProductSpecCarrierCreateWizardZone(models.TransientModel):
    """Zone tarifaire transiente (étape 2b du wizard de création)."""
    _name        = "product.spec.carrier.create.wizard.zone"
    _description = "Zone (wizard transporteur)"
    _order       = "sequence, name"

    wizard_id     = fields.Many2one(
        "product.spec.carrier.create.wizard", required=True, ondelete="cascade"
    )
    name          = fields.Char(string="Zone", required=True, default="France")
    sequence      = fields.Integer(default=10)
    threshold_ids = fields.One2many(
        "product.spec.carrier.create.wizard.threshold", "zone_id",
        string="Paliers tarifaires",
    )


class ProductSpecCarrierCreateWizardThreshold(models.TransientModel):
    """Palier tarifaire transient (étape 2b du wizard de création)."""
    _name        = "product.spec.carrier.create.wizard.threshold"
    _description = "Palier (wizard transporteur)"
    _order       = "zone_id, max_weight_g"

    zone_id      = fields.Many2one(
        "product.spec.carrier.create.wizard.zone", required=True, ondelete="cascade"
    )
    max_weight_g = fields.Integer(
        string="Poids max (g)", required=True,
        help="Ce palier s'applique aux colis jusqu'à ce poids inclus.",
    )
    price_eur    = fields.Float(string="Tarif HT (€)", digits=(10, 2), required=True)

    @api.depends("max_weight_g")
    def _compute_display(self):
        for rec in self:
            if rec.max_weight_g >= 1000:
                rec.max_weight_display = f"{rec.max_weight_g / 1000:.3g} kg"
            else:
                rec.max_weight_display = f"{rec.max_weight_g} g"

    max_weight_display = fields.Char(compute="_compute_display", store=False)
