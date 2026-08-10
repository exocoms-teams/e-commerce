# -*- coding: utf-8 -*-
import json
import logging
from odoo import _, api, fields, models
from odoo.exceptions import UserError

_logger = logging.getLogger(__name__)

# URLs par défaut de chaque provider
PROVIDER_API_URLS = {
    "colissimo":  "https://api.laposte.fr/colissimo/v2",
    "chronopost": "https://www.chronopost.fr/shipping-cxf/ShippingServiceWS",
    "dhl":        "https://api.dhl.com/ecs/pcs",
    "ups":        "https://onlinetools.ups.com/api",
    "gls":        "https://api.gls-group.eu",
    "custom":     "",
}

PROVIDER_SELECTION = [
    ("none",       "Grille statique uniquement"),
    ("colissimo",  "Colissimo (La Poste)"),
    ("chronopost", "Chronopost"),
    ("dhl",        "DHL Express"),
    ("ups",        "UPS"),
    ("gls",        "GLS"),
    ("custom",     "Transporteur personnalisé"),
]


class ProductSpecCarrier(models.Model):
    _name        = "product.spec.carrier"
    _description = "Transporteur (frais de port)"
    _order       = "sequence, name"

    # ── Champs de base ─────────────────────────────────────────────
    name               = fields.Char(string="Transporteur", required=True)
    sequence           = fields.Integer(default=10)
    active             = fields.Boolean(default=True)
    volumetric_divisor = fields.Integer(
        string="Diviseur volumétrique", default=5000,
        help="Poids volumétrique (kg) = L×l×H (cm) / diviseur.\n"
             "Standard route : 5000 · Standard aérien : 6000",
    )
    max_weight_kg      = fields.Float(string="Poids maximum (kg)", default=30.0)
    note               = fields.Char(string="Note / conditions")
    zone_ids           = fields.One2many("product.spec.carrier.zone", "carrier_id", string="Zones")
    zone_count         = fields.Integer(compute="_compute_zone_count", string="Nb zones")

    @api.depends("zone_ids")
    def _compute_zone_count(self):
        for rec in self:
            rec.zone_count = len(rec.zone_ids)

    # ── Connexion API ──────────────────────────────────────────────
    api_provider    = fields.Selection(
        PROVIDER_SELECTION, string="Fournisseur API", default="none",
        help="Choisissez le provider pour obtenir des tarifs en temps réel.",
    )
    api_base_url    = fields.Char(
        string="URL de base API",
        help="URL racine de l'API. Pré-remplie automatiquement selon le provider.",
    )
    api_account_no  = fields.Char(string="Numéro de compte / contrat")
    api_key         = fields.Char(
        string="Clé API / Client ID",
        help="Clé API ou Client ID fourni par le transporteur.",
    )
    api_secret      = fields.Char(
        string="Secret / Token",
        help="Secret ou token d'API.",
    )
    api_timeout     = fields.Integer(string="Timeout (s)", default=8)
    api_depot_code  = fields.Char(string="Code agence / dépôt")
    api_use_live    = fields.Boolean(
        string="Utiliser les tarifs en temps réel",
        default=False,
        help="Si actif, interroge l'API du transporteur à chaque calcul de frais de port.",
    )
    api_fallback    = fields.Boolean(
        string="Fallback sur la grille statique si API indisponible",
        default=True,
    )
    api_last_check  = fields.Datetime(string="Dernière vérification", readonly=True)
    api_last_status = fields.Selection(
        [("ok", "Connectée"), ("error", "Erreur"), ("untested", "Non testée")],
        string="Statut API", default="untested", readonly=True,
    )
    api_last_message = fields.Char(string="Dernier message API", readonly=True)

    # ── Onchange provider → pré-remplir l'URL ─────────────────────
    @api.onchange("api_provider")
    def _onchange_api_provider(self):
        if self.api_provider and self.api_provider != "none":
            self.api_base_url = PROVIDER_API_URLS.get(self.api_provider, "")

    # ── Test de connexion ─────────────────────────────────────────
    def action_test_api(self):
        """Teste la connexion API et enregistre le résultat."""
        self.ensure_one()
        if self.api_provider == "none" or not self.api_provider:
            raise UserError(_("Sélectionnez un fournisseur API avant de tester."))

        ok, message, price = self._call_api_test()

        self.api_last_check   = fields.Datetime.now()
        self.api_last_status  = "ok" if ok else "error"
        self.api_last_message = message

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

    def _call_api_test(self):
        """
        Appelle l'API du transporteur avec un envoi test (500 g, France).
        Retourne (succès: bool, message: str, tarif_test: float|None).
        """
        try:
            import requests as _req
        except ImportError:
            return False, "Module 'requests' manquant. pip install requests", None

        provider = self.api_provider
        key      = self.api_key or ""
        secret   = self.api_secret or ""
        account  = self.api_account_no or ""
        base_url = (self.api_base_url or "").rstrip("/")
        timeout  = self.api_timeout or 8

        try:
            if provider == "colissimo":
                return self._test_colissimo(_req, base_url, account, key, timeout)
            elif provider == "dhl":
                return self._test_dhl(_req, base_url, key, secret, account, timeout)
            elif provider == "ups":
                return self._test_ups(_req, base_url, key, secret, account, timeout)
            elif provider == "gls":
                return self._test_gls(_req, base_url, key, secret, timeout)
            elif provider == "chronopost":
                return self._test_chronopost(_req, base_url, account, key, timeout)
            elif provider == "custom":
                return self._test_custom(_req, base_url, key, timeout)
            else:
                return False, "Provider non reconnu.", None
        except Exception as e:
            _logger.warning("Carrier API test error [%s]: %s", provider, e)
            return False, str(e)[:200], None

    # ── Implémentations par provider ───────────────────────────────

    def _test_colissimo(self, req, base_url, account, key, timeout):
        """
        Colissimo — API La Poste
        Doc : https://developer.laposte.fr/products/colissimo
        Endpoint test : POST /calculateProductsOffer
        """
        url  = f"{base_url}/calculateProductsOffer"
        body = {
            "contractNumber": account,
            "password":       key,
            "sender":   {"senderParcelRef": "TEST-EXOCOMS", "address": {"countryCode": "FR"}},
            "addressee":{"address": {"countryCode": "FR"}},
            "parcel":   {"weight": 0.5, "insuranceValue": 0},
            "letter":   {"service": {"productCode": "DOM", "depositDate": "2026-01-01",
                                     "orderNumber": "TEST"}, "archive": False},
        }
        resp = req.post(url, json=body, timeout=timeout)
        if resp.status_code == 200:
            data  = resp.json()
            price = data.get("offerResponse", [{}])[0].get("totalAmountTTC") if data.get("offerResponse") else None
            return True, f"Connexion OK — Colissimo DOM 500g : {price} €" if price else "Connexion OK", price
        return False, f"HTTP {resp.status_code} : {resp.text[:150]}", None

    def _test_dhl(self, req, base_url, key, secret, account, timeout):
        """
        DHL Express — API myDHL
        Doc : https://developer.dhl.com/api-reference/dhl-express-rating
        Auth : Basic (key:secret)
        """
        url  = f"{base_url}/rates"
        body = {
            "customerDetails": {
                "shipperDetails": {"postalCode": "75001", "cityName": "Paris",
                                   "countryCode": "FR", "addressLine1": "1 rue test",
                                   "accountNumber": account},
                "receiverDetails": {"postalCode": "69001", "cityName": "Lyon",
                                    "countryCode": "FR", "addressLine1": "2 rue test"},
            },
            "accounts": [{"number": account, "typeCode": "shipper"}],
            "productCode": "N",
            "localProductCode": "N",
            "plannedShippingDateAndTime": "2026-01-01T12:00:00 GMT+02:00",
            "unitOfMeasurement": "metric",
            "packages": [{"weight": 0.5, "dimensions": {"length": 20, "width": 15, "height": 10}}],
        }
        resp = req.post(url, json=body, timeout=timeout,
                        headers={"Content-Type": "application/json",
                                 "Accept": "application/json"},
                        auth=(key, secret))
        if resp.status_code in (200, 201):
            data  = resp.json()
            price = (data.get("products", [{}])[0].get("totalPrice", [{}])[0].get("price")
                     if data.get("products") else None)
            return True, f"Connexion OK — DHL 500g France : {price}" if price else "Connexion OK", price
        return False, f"HTTP {resp.status_code} : {resp.text[:150]}", None

    def _test_ups(self, req, base_url, key, secret, account, timeout):
        """
        UPS — API Rating (OAuth2)
        Doc : https://developer.ups.com/api/reference/rating
        On obtient d'abord un token, puis on appelle /rating
        """
        # Étape 1 : token OAuth2
        token_resp = req.post(
            "https://onlinetools.ups.com/security/v1/oauth/token",
            data={"grant_type": "client_credentials"},
            auth=(key, secret),
            timeout=timeout,
        )
        if token_resp.status_code != 200:
            return False, f"Auth UPS échouée : HTTP {token_resp.status_code}", None
        token = token_resp.json().get("access_token", "")

        # Étape 2 : demande de tarif test
        url  = f"{base_url}/rating/v2205/rate"
        body = {
            "RateRequest": {
                "Shipment": {
                    "Shipper":   {"ShipperNumber": account, "Address": {"CountryCode": "FR"}},
                    "ShipTo":    {"Address": {"CountryCode": "FR"}},
                    "Service":   {"Code": "11"},
                    "Package":   [{"PackagingType": {"Code": "02"},
                                   "PackageWeight": {"Weight": "0.5",
                                                     "UnitOfMeasurement": {"Code": "KGS"}}}],
                }
            }
        }
        resp = req.post(url, json=body, timeout=timeout,
                        headers={"Authorization": f"Bearer {token}",
                                 "Content-Type": "application/json"})
        if resp.status_code == 200:
            return True, "Connexion UPS OK", None
        return False, f"HTTP {resp.status_code} : {resp.text[:150]}", None

    def _test_gls(self, req, base_url, key, secret, timeout):
        """GLS — REST API (Basic auth)."""
        url  = f"{base_url}/public/v1/shipments/parcel-prices"
        resp = req.get(url, timeout=timeout, auth=(key, secret))
        if resp.status_code in (200, 201):
            return True, "Connexion GLS OK", None
        return False, f"HTTP {resp.status_code} : {resp.text[:150]}", None

    def _test_chronopost(self, req, base_url, account, key, timeout):
        """Chronopost — vérification par ping de l'endpoint."""
        resp = req.get(base_url + "?wsdl", timeout=timeout)
        if resp.status_code == 200:
            return True, "Endpoint Chronopost accessible", None
        return False, f"HTTP {resp.status_code}", None

    def _test_custom(self, req, base_url, key, timeout):
        """Transporteur personnalisé — simple GET sur l'URL de base."""
        if not base_url:
            return False, "Renseignez l'URL de base avant de tester.", None
        resp = req.get(base_url, timeout=timeout,
                       headers={"Authorization": f"Bearer {key}"} if key else {})
        if resp.status_code < 400:
            return True, f"URL accessible (HTTP {resp.status_code})", None
        return False, f"HTTP {resp.status_code} : {resp.text[:100]}", None

    # ── Tarif live ─────────────────────────────────────────────────
    def get_live_rate(self, weight_kg, zone_name="France"):
        """
        Interroge l'API en temps réel pour un poids et une zone donnés.
        Retourne (prix: float|None, source: str).
        source = 'live' | 'static' | 'none'
        """
        self.ensure_one()
        if not self.api_use_live or self.api_provider == "none":
            return None, "none"

        try:
            import requests as _req
            price = self._fetch_live_rate(_req, weight_kg, zone_name)
            if price is not None:
                return price, "live"
        except Exception as e:
            _logger.warning("Live rate error [%s/%s]: %s", self.name, zone_name, e)

        # Fallback sur la grille statique
        if self.api_fallback:
            zone = self.zone_ids.filtered(lambda z: z.name == zone_name)
            if zone:
                price = zone[0].get_price(weight_kg * 1000)
                if price is not None:
                    return price, "static"
        return None, "none"

    def _fetch_live_rate(self, req, weight_kg, zone_name):
        """Appelle l'API et renvoie le tarif brut."""
        provider = self.api_provider
        if provider == "colissimo":
            return self._live_colissimo(req, weight_kg, zone_name)
        if provider == "dhl":
            return self._live_dhl(req, weight_kg, zone_name)
        if provider == "ups":
            return self._live_ups(req, weight_kg, zone_name)
        return None

    def _live_colissimo(self, req, weight_kg, zone_name):
        base_url = (self.api_base_url or PROVIDER_API_URLS["colissimo"]).rstrip("/")
        # Code produit selon zone
        product_code = "DOM" if "france" in zone_name.lower() else "COLIS"
        body = {
            "contractNumber": self.api_account_no or "",
            "password":       self.api_key or "",
            "sender":         {"senderParcelRef": "EXOCOMS",
                               "address": {"countryCode": "FR"}},
            "addressee":      {"address": {"countryCode": "FR"
                               if "france" in zone_name.lower() else "DE"}},
            "parcel":         {"weight": round(weight_kg, 3)},
            "letter":         {"service": {"productCode": product_code,
                                           "depositDate": "2026-01-01",
                                           "orderNumber": "EXOCOMS"},
                               "archive": False},
        }
        resp = req.post(f"{base_url}/calculateProductsOffer",
                        json=body, timeout=self.api_timeout or 8)
        if resp.status_code == 200:
            data = resp.json()
            offers = data.get("offerResponse", [])
            if offers:
                return offers[0].get("totalAmountTTC")
        return None

    def _live_dhl(self, req, weight_kg, zone_name):
        base_url = (self.api_base_url or PROVIDER_API_URLS["dhl"]).rstrip("/")
        country  = "DE" if "europe" in zone_name.lower() else "FR"
        body = {
            "customerDetails": {
                "shipperDetails": {"postalCode": "75001", "cityName": "Paris",
                                   "countryCode": "FR", "addressLine1": "1 rue test",
                                   "accountNumber": self.api_account_no or ""},
                "receiverDetails": {"postalCode": "10115", "cityName": "Berlin",
                                    "countryCode": country, "addressLine1": "2 str test"},
            },
            "accounts":    [{"number": self.api_account_no or "", "typeCode": "shipper"}],
            "productCode": "N",
            "localProductCode": "N",
            "plannedShippingDateAndTime": "2026-01-01T12:00:00 GMT+02:00",
            "unitOfMeasurement": "metric",
            "packages": [{"weight": round(weight_kg, 3),
                          "dimensions": {"length": 30, "width": 20, "height": 15}}],
        }
        resp = req.post(f"{base_url}/rates", json=body,
                        timeout=self.api_timeout or 8,
                        auth=(self.api_key or "", self.api_secret or ""),
                        headers={"Content-Type": "application/json"})
        if resp.status_code == 200:
            products = resp.json().get("products", [])
            if products:
                prices = products[0].get("totalPrice", [])
                if prices:
                    return prices[0].get("price")
        return None

    def _live_ups(self, req, weight_kg, zone_name):
        # OAuth2 token
        token_resp = req.post(
            "https://onlinetools.ups.com/security/v1/oauth/token",
            data={"grant_type": "client_credentials"},
            auth=(self.api_key or "", self.api_secret or ""),
            timeout=self.api_timeout or 8,
        )
        if token_resp.status_code != 200:
            return None
        token = token_resp.json().get("access_token", "")
        base_url = (self.api_base_url or PROVIDER_API_URLS["ups"]).rstrip("/")
        country  = "DE" if "europe" in zone_name.lower() else "FR"
        body = {
            "RateRequest": {
                "Shipment": {
                    "Shipper":  {"ShipperNumber": self.api_account_no or "",
                                 "Address": {"CountryCode": "FR"}},
                    "ShipTo":   {"Address": {"CountryCode": country}},
                    "Service":  {"Code": "11"},
                    "Package":  [{"PackagingType": {"Code": "02"},
                                  "PackageWeight": {
                                      "Weight": str(round(weight_kg, 3)),
                                      "UnitOfMeasurement": {"Code": "KGS"}}}],
                }
            }
        }
        resp = req.post(f"{base_url}/rating/v2205/rate", json=body,
                        timeout=self.api_timeout or 8,
                        headers={"Authorization": f"Bearer {token}",
                                 "Content-Type": "application/json"})
        if resp.status_code == 200:
            try:
                return float(resp.json()["RateResponse"]["RatedShipment"][0]
                             ["TotalCharges"]["MonetaryValue"])
            except (KeyError, IndexError, TypeError):
                pass
        return None


class ProductSpecCarrierZone(models.Model):
    _name        = "product.spec.carrier.zone"
    _description = "Zone tarifaire transporteur"
    _order       = "carrier_id, sequence, name"

    carrier_id    = fields.Many2one("product.spec.carrier", required=True, ondelete="cascade")
    name          = fields.Char(string="Zone", required=True)
    sequence      = fields.Integer(default=10)
    threshold_ids = fields.One2many(
        "product.spec.carrier.zone.threshold", "zone_id", string="Grille tarifaire"
    )

    def get_price(self, weight_g: float):
        """Renvoie le tarif HT en € depuis la grille statique, ou None si hors gabarit."""
        self.ensure_one()
        for t in self.threshold_ids.sorted("max_weight_g"):
            if weight_g <= t.max_weight_g:
                return t.price_eur
        return None


class ProductSpecCarrierZoneThreshold(models.Model):
    _name        = "product.spec.carrier.zone.threshold"
    _description = "Palier tarifaire"
    _order       = "zone_id, max_weight_g"

    zone_id      = fields.Many2one("product.spec.carrier.zone", required=True, ondelete="cascade")
    max_weight_g = fields.Integer(string="Poids max (g)", required=True)
    max_weight_display = fields.Char(compute="_compute_display", store=False)
    price_eur    = fields.Float(string="Tarif HT (€)", digits=(10, 2), required=True)

    @api.depends("max_weight_g")
    def _compute_display(self):
        for rec in self:
            if rec.max_weight_g >= 1000:
                rec.max_weight_display = f"{rec.max_weight_g / 1000:.3g} kg"
            else:
                rec.max_weight_display = f"{rec.max_weight_g} g"
