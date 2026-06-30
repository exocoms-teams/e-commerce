import logging

from odoo import api, fields, models

_logger = logging.getLogger(__name__)


class ProductTemplate(models.Model):
    _inherit = 'product.template'

    is_telecom_only = fields.Boolean(
        string="Télécom uniquement",
        help="Produit visible uniquement sur la page /telecom et masqué du shop.",
    )
    kissgroup_plan_code = fields.Char(
        string="Code forfait KISSGROUP", index=True, copy=False,
    )
    kissgroup_provider = fields.Char(string="Opérateur KISSGROUP")
    kissgroup_setup_fee = fields.Float(string="Frais d'activation HT")
    kissgroup_supports_esim = fields.Boolean(string="eSIM supportée")

    @api.model
    def _kissgroup_plan_to_vals(self, plan):
        """Map a KISSGROUP mobile plan dict to product.template values."""
        provider = (plan.get('provider') or '').strip()
        monthly = float(plan.get('monthly_price_eur') or 0.0)
        setup = float(plan.get('setup_fee_eur') or 0.0)

        desc = []
        if provider:
            desc.append("Opérateur : %s" % provider.capitalize())
        desc.append("%.2f €/mois HT" % monthly)
        if setup:
            desc.append("Frais d'activation : %.2f € HT" % setup)
        if plan.get('supports_esim'):
            desc.append("eSIM disponible")

        return {
            'name': plan.get('plan_name') or plan.get('plan_code'),
            'type': 'service',
            'sale_ok': True,
            'is_published': True,
            'is_telecom_only': True,
            'list_price': monthly,
            'description_sale': " • ".join(desc),
            'kissgroup_provider': provider or False,
            'kissgroup_setup_fee': setup,
            'kissgroup_supports_esim': bool(plan.get('supports_esim')),
        }

    @api.model
    def _cron_sync_kissgroup_mobile_plans(self):
        """Upsert KISSGROUP mobile plans into product.template.

        Run by an ir.cron. Safe to call even when no API key is configured
        (it logs and returns without raising).
        """
        api = self.env['telecom.kissgroup.api']
        if not api._get_credentials()[0]:
            _logger.info("KISSGROUP sync skipped: API key not configured.")
            return False

        plans = api.get_mobile_plans()
        Product = self.with_context(active_test=False)
        seen_codes = []
        created = updated = 0

        for plan in plans:
            code = plan.get('plan_code')
            if not code:
                continue
            seen_codes.append(code)
            vals = self._kissgroup_plan_to_vals(plan)
            product = Product.search([('kissgroup_plan_code', '=', code)], limit=1)
            if product:
                if not product.active:
                    vals['active'] = True
                product.write(vals)
                updated += 1
            else:
                vals['kissgroup_plan_code'] = code
                Product.create(vals)
                created += 1

        # Retire plans no longer offered by KISSGROUP.
        obsolete = Product.search([
            ('kissgroup_plan_code', '!=', False),
            ('kissgroup_plan_code', 'not in', seen_codes or ['__none__']),
            ('active', '=', True),
        ])
        if obsolete:
            obsolete.write({'is_published': False, 'active': False})

        _logger.info(
            "KISSGROUP mobile sync: %s created, %s updated, %s retired.",
            created, updated, len(obsolete),
        )
        return True
