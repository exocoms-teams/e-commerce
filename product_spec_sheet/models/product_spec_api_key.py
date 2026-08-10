# -*- coding: utf-8 -*-
import secrets
from odoo import _, api, fields, models
from odoo.exceptions import UserError


class ProductSpecApiKey(models.Model):
    """
    Clé d'accès à l'API REST du catalogue.
    Chaque revendeur ou partenaire reçoit sa propre clé, avec ses permissions
    et ses restrictions (catégories, quota, adresses IP).
    """
    _name        = "product.spec.api.key"
    _description = "Clé API catalogue"
    _order       = "create_date desc"
    _inherit     = ["mail.thread"]

    name       = fields.Char(string="Nom", required=True, tracking=True,
                             help="Ex : Revendeur Dupont, Intégration site partenaire")
    partner_id = fields.Many2one("res.partner", string="Partenaire", tracking=True)
    active     = fields.Boolean(default=True, tracking=True)

    api_key = fields.Char(
        string="Clé API", readonly=True, copy=False, index=True,
        default=lambda self: "psk_" + secrets.token_urlsafe(32),
    )

    # ── Permissions ───────────────────────────────────────────────
    allow_products = fields.Boolean(string="Lecture des produits", default=True)
    allow_specs    = fields.Boolean(string="Lecture des caractéristiques", default=True)
    allow_stock    = fields.Boolean(string="Lecture des stocks", default=False)
    allow_prices   = fields.Boolean(string="Lecture des prix", default=True)
    allow_shipping = fields.Boolean(
        string="Calcul des frais de port", default=False,
        help="Autorise l'appel à l'endpoint de calcul de frais de port.",
    )

    # ── Restrictions ──────────────────────────────────────────────
    categ_ids = fields.Many2many(
        "product.category", string="Catégories autorisées",
        help="Laisser vide pour donner accès à tout le catalogue.",
    )
    price_markup = fields.Float(
        string="Majoration prix (%)", default=0.0,
        help="Prix renvoyés majorés de ce pourcentage pour ce partenaire.",
    )
    ip_whitelist = fields.Char(
        string="IP autorisées",
        help="Adresses IP séparées par des virgules. Vide = toutes autorisées.",
    )
    rate_limit_hour = fields.Integer(
        string="Quota horaire", default=1000,
        help="Nombre maximum de requêtes par heure. 0 = illimité.",
    )
    expiry_date = fields.Date(string="Date d'expiration", tracking=True)

    # ── Suivi ─────────────────────────────────────────────────────
    call_count      = fields.Integer(string="Appels totaux", readonly=True)
    last_call_date  = fields.Datetime(string="Dernier appel", readonly=True)
    last_call_ip    = fields.Char(string="Dernière IP", readonly=True)
    log_ids         = fields.One2many(
        "product.spec.api.log", "api_key_id", string="Journal des appels",
    )

    _sql_constraints = [
        ("uniq_api_key", "unique(api_key)", "Cette clé API existe déjà."),
    ]

    def action_regenerate_key(self):
        """Régénère la clé — invalide immédiatement l'ancienne."""
        for rec in self:
            rec.api_key = "psk_" + secrets.token_urlsafe(32)
            rec.message_post(body=_("Clé API régénérée. L'ancienne clé est invalidée."))
        return True

    def action_view_logs(self):
        self.ensure_one()
        return {
            "type": "ir.actions.act_window",
            "name": _("Journal des appels — %s") % self.name,
            "res_model": "product.spec.api.log",
            "view_mode": "list",
            "domain": [("api_key_id", "=", self.id)],
        }

    # ── Validation d'un appel ─────────────────────────────────────
    @api.model
    def authenticate(self, key_value, remote_ip=None):
        """
        Valide une clé API. Renvoie (record|None, message_erreur|None).
        """
        if not key_value:
            return None, "Clé API manquante"

        key = self.sudo().search([("api_key", "=", key_value)], limit=1)
        if not key:
            return None, "Clé API invalide"
        if not key.active:
            return None, "Clé API désactivée"
        if key.expiry_date and key.expiry_date < fields.Date.context_today(key):
            return None, "Clé API expirée"

        if key.ip_whitelist and remote_ip:
            allowed = [ip.strip() for ip in key.ip_whitelist.split(",") if ip.strip()]
            if allowed and remote_ip not in allowed:
                return None, "Adresse IP non autorisée"

        if key.rate_limit_hour:
            from datetime import timedelta
            since = fields.Datetime.now() - timedelta(hours=1)
            recent = self.env["product.spec.api.log"].sudo().search_count([
                ("api_key_id", "=", key.id),
                ("create_date", ">=", since),
            ])
            if recent >= key.rate_limit_hour:
                return None, "Quota horaire dépassé"

        return key, None

    def log_call(self, endpoint, status, remote_ip=None, duration_ms=0):
        """Enregistre un appel dans le journal."""
        self.ensure_one()
        self.sudo().write({
            "call_count":     self.call_count + 1,
            "last_call_date": fields.Datetime.now(),
            "last_call_ip":   remote_ip or self.last_call_ip,
        })
        self.env["product.spec.api.log"].sudo().create({
            "api_key_id":  self.id,
            "endpoint":    endpoint,
            "status_code": status,
            "remote_ip":   remote_ip or "",
            "duration_ms": duration_ms,
        })


class ProductSpecApiLog(models.Model):
    """Journal des appels à l'API REST."""
    _name        = "product.spec.api.log"
    _description = "Appel API catalogue"
    _order       = "create_date desc"

    api_key_id  = fields.Many2one(
        "product.spec.api.key", string="Clé", required=True,
        ondelete="cascade", index=True,
    )
    partner_id  = fields.Many2one(
        related="api_key_id.partner_id", store=True, string="Partenaire",
    )
    endpoint    = fields.Char(string="Endpoint", index=True)
    status_code = fields.Integer(string="Code HTTP")
    remote_ip   = fields.Char(string="IP")
    duration_ms = fields.Integer(string="Durée (ms)")
