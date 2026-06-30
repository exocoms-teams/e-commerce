import logging

from odoo import api, fields, models

_logger = logging.getLogger(__name__)


class ProductTemplate(models.Model):
    _inherit = 'product.template'

    is_telecom_only = fields.Boolean(
        string="Télécom uniquement",
        help="Produit visible uniquement sur la page /telecom et masqué du shop.",
    )
    kissgroup_code = fields.Char(
        string="Code KISSGROUP", index=True, copy=False,
        help="Identifiant stable de l'offre chez KISSGROUP (plan_code, pack_code...).",
    )
    kissgroup_kind = fields.Selection(
        selection=[
            ('mobile_plan', "Forfait mobile"),
            ('sim_pack', "Pack SIM"),
        ],
        string="Type d'offre KISSGROUP",
    )
    kissgroup_provider = fields.Char(string="Opérateur KISSGROUP")
    kissgroup_setup_fee = fields.Float(
        string="Frais ponctuels HT",
        help="Frais d'activation (forfait) ou frais de livraison (pack SIM), HT.",
    )
    kissgroup_supports_esim = fields.Boolean(string="eSIM supportée")

    # ------------------------------------------------------------------
    # Mapping API -> product.template values
    # ------------------------------------------------------------------
    @api.model
    def _map_mobile_plan(self, plan):
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
            'kissgroup_kind': 'mobile_plan',
            'kissgroup_code': plan.get('plan_code'),
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
    def _map_sim_pack(self, pack):
        provider = (pack.get('provider') or '').strip()
        quantity = pack.get('quantity') or 0
        price = float(pack.get('price_eur') or 0.0)
        shipping = float(pack.get('shipping_fee_eur') or 0.0)

        name = pack.get('description') or (
            "Pack %s SIM%s" % (quantity, " %s" % provider.capitalize() if provider else "")
        )
        desc = []
        if quantity:
            desc.append("%s carte(s) SIM" % quantity)
        if provider:
            desc.append("Opérateur : %s" % provider.capitalize())
        desc.append("%.2f € HT" % price)
        if shipping:
            desc.append("Livraison : %.2f € HT" % shipping)

        return {
            'kissgroup_kind': 'sim_pack',
            'kissgroup_code': pack.get('pack_code'),
            'name': name,
            'type': 'consu',
            'sale_ok': True,
            'is_published': True,
            'is_telecom_only': True,
            'list_price': price,
            'description_sale': " • ".join(desc),
            'kissgroup_provider': provider or False,
            'kissgroup_setup_fee': shipping,
            'kissgroup_supports_esim': False,
        }

    @api.model
    def _kissgroup_catalogue_sources(self):
        """Map each KISSGROUP catalogue kind to a builder returning a list of
        product.template value dicts. Add a new catalogue here to expose it."""
        api = self.env['telecom.kissgroup.api']
        return {
            'mobile_plan': lambda: [self._map_mobile_plan(p) for p in api.get_mobile_plans()],
            'sim_pack': lambda: [self._map_sim_pack(p) for p in api.get_sim_packs()],
        }

    # ------------------------------------------------------------------
    # Cron
    # ------------------------------------------------------------------
    @api.model
    def _cron_sync_kissgroup_catalogue(self):
        """Upsert every KISSGROUP catalogue into product.template.

        Run by an ir.cron. Safe to call without an API key (logs and returns).
        """
        api = self.env['telecom.kissgroup.api']
        if not api._get_credentials()[0]:
            _logger.info("KISSGROUP sync skipped: API key not configured.")
            return False

        Product = self.with_context(active_test=False)
        totals = {'created': 0, 'updated': 0, 'retired': 0}

        for kind, build in self._kissgroup_catalogue_sources().items():
            seen_codes = []
            for vals in build():
                code = vals.get('kissgroup_code')
                if not code:
                    continue
                seen_codes.append(code)
                product = Product.search([
                    ('kissgroup_kind', '=', kind),
                    ('kissgroup_code', '=', code),
                ], limit=1)
                if product:
                    if not product.active:
                        vals['active'] = True
                    product.write(vals)
                    totals['updated'] += 1
                else:
                    Product.create(vals)
                    totals['created'] += 1

            obsolete = Product.search([
                ('kissgroup_kind', '=', kind),
                ('kissgroup_code', 'not in', seen_codes or ['__none__']),
                ('active', '=', True),
            ])
            if obsolete:
                obsolete.write({'is_published': False, 'active': False})
                totals['retired'] += len(obsolete)

        _logger.info(
            "KISSGROUP catalogue sync: %(created)s created, %(updated)s updated, "
            "%(retired)s retired.", totals,
        )
        return True
