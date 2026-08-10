# -*- coding: utf-8 -*-
import logging
from odoo import _, api, fields, models

_logger = logging.getLogger(__name__)


class DeliveryCarrier(models.Model):
    """
    Ajoute un type de livraison 'spec_carrier' qui utilise les transporteurs
    et grilles tarifaires du module product_spec_sheet, avec support du
    poids volumétrique et des tarifs API en temps réel.
    """
    _inherit = "delivery.carrier"

    delivery_type = fields.Selection(
        selection_add=[("spec_carrier", "Transporteur (caractéristiques produit)")],
        ondelete={"spec_carrier": "set default"},
    )
    spec_carrier_id = fields.Many2one(
        "product.spec.carrier",
        string="Transporteur",
        help="Transporteur configuré dans Ventes > Configuration > Transporteurs.",
    )
    spec_carrier_zone_id = fields.Many2one(
        "product.spec.carrier.zone",
        string="Zone tarifaire",
        domain="[('carrier_id','=',spec_carrier_id)]",
        help="Zone à utiliser pour ce mode de livraison.",
    )
    spec_use_volumetric = fields.Boolean(
        string="Appliquer le poids volumétrique",
        default=True,
        help="Facture le plus élevé entre poids réel et poids volumétrique.",
    )
    spec_margin_percent = fields.Float(
        string="Marge appliquée (%)",
        default=0.0,
        help="Marge ajoutée au tarif transporteur. Ex : 10 pour +10%.",
    )

    @api.onchange("spec_carrier_id")
    def _onchange_spec_carrier(self):
        """Réinitialise la zone si le transporteur change."""
        if self.spec_carrier_zone_id.carrier_id != self.spec_carrier_id:
            self.spec_carrier_zone_id = False

    # ── Calcul du poids facturé ───────────────────────────────────
    def _spec_get_billed_weight(self, order=None, picking=None):
        """
        Calcule le poids facturé (kg) en tenant compte du poids volumétrique.
        Retourne (poids_facturé, poids_réel, poids_volumétrique, alerte).
        """
        self.ensure_one()
        carrier = self.spec_carrier_id
        divisor = (carrier.volumetric_divisor or 5000) if carrier else 5000

        real_kg = 0.0
        vol_kg = 0.0
        missing = []

        lines = []
        if order:
            lines = [
                (l.product_id, l.product_uom_qty)
                for l in order.order_line
                if l.product_id and l.product_id.type in ("consu", "product")
                and not l.is_delivery
            ]
        elif picking:
            lines = [(m.product_id, m.quantity) for m in picking.move_ids]

        for product, qty in lines:
            if product.weight:
                real_kg += product.weight * qty
            else:
                missing.append(product.display_name)

            # volume Odoo en m³ → cm³ → poids volumétrique
            if product.volume:
                vol_cm3 = product.volume * 1_000_000
                vol_kg += (vol_cm3 / divisor) * qty

        billed = max(real_kg, vol_kg) if self.spec_use_volumetric else real_kg
        return billed, real_kg, vol_kg, missing

    # ── Tarif pour un devis ───────────────────────────────────────
    def spec_carrier_rate_shipment(self, order):
        """Calcule le tarif de livraison pour une commande."""
        self.ensure_one()
        carrier = self.spec_carrier_id
        zone = self.spec_carrier_zone_id

        if not carrier or not zone:
            return {
                "success": False,
                "price": 0.0,
                "error_message": _("Transporteur ou zone non configuré sur ce mode de livraison."),
                "warning_message": False,
            }

        billed_kg, real_kg, vol_kg, missing = self._spec_get_billed_weight(order=order)

        if billed_kg <= 0:
            return {
                "success": False,
                "price": 0.0,
                "error_message": _(
                    "Poids introuvable pour les produits de cette commande. "
                    "Complétez le poids dans Ventes > Configuration > Qualité des fiches."
                ),
                "warning_message": False,
            }

        # Dépassement du gabarit
        if carrier.max_weight_kg and billed_kg > carrier.max_weight_kg:
            return {
                "success": False,
                "price": 0.0,
                "error_message": _(
                    "Poids facturé (%(w).3f kg) supérieur au maximum accepté par %(c)s (%(m).1f kg).",
                    w=billed_kg, c=carrier.name, m=carrier.max_weight_kg,
                ),
                "warning_message": False,
            }

        # 1. Tarif live via API si activé
        price = None
        source = "static"
        if carrier.api_use_live and carrier.api_provider not in ("none", False, ""):
            live_price, live_src = carrier.get_live_rate(billed_kg, zone.name)
            if live_price is not None:
                price, source = live_price, live_src

        # 2. Grille statique
        if price is None:
            price = zone.get_price(billed_kg * 1000)

        if price is None:
            return {
                "success": False,
                "price": 0.0,
                "error_message": _(
                    "Aucun palier tarifaire pour %(w).3f kg dans la zone %(z)s.",
                    w=billed_kg, z=zone.name,
                ),
                "warning_message": False,
            }

        # Marge commerciale
        if self.spec_margin_percent:
            price = price * (1 + self.spec_margin_percent / 100.0)

        warning = False
        notes = []
        if self.spec_use_volumetric and vol_kg > real_kg:
            notes.append(_(
                "Poids volumétrique appliqué (%(v).3f kg au lieu de %(r).3f kg).",
                v=vol_kg, r=real_kg,
            ))
        if missing:
            notes.append(_(
                "Poids manquant sur : %s.", ", ".join(missing[:3])
            ))
        if source == "live":
            notes.append(_("Tarif obtenu en temps réel depuis l'API %s.", carrier.name))
        if notes:
            warning = " ".join(notes)

        return {
            "success": True,
            "price": price,
            "error_message": False,
            "warning_message": warning,
        }

    # ── Expédition (bon de livraison) ─────────────────────────────
    def spec_carrier_send_shipping(self, pickings):
        """Retourne le coût pour chaque bon de livraison."""
        result = []
        for picking in pickings:
            billed_kg, _real, _vol, _missing = self._spec_get_billed_weight(picking=picking)
            zone = self.spec_carrier_zone_id
            price = zone.get_price(billed_kg * 1000) if zone else 0.0
            if price and self.spec_margin_percent:
                price = price * (1 + self.spec_margin_percent / 100.0)
            result.append({
                "exact_price": price or 0.0,
                "tracking_number": False,
            })
        return result

    def spec_carrier_cancel_shipment(self, pickings):
        """Annulation — rien à faire côté transporteur pour ce mode."""
        return True

    def spec_carrier_get_tracking_link(self, picking):
        """Pas de suivi automatique pour ce mode de livraison."""
        return False
