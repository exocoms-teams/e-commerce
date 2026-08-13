from odoo.tests.common import TransactionCase
from ..controllers.dashboard_api import TrendDashboardAPI


class TestSubscriptionGroupAssignment(TransactionCase):
    """WIN-66 : vérifie que la validation d'une facture liée à une commande
    d'abonnement (sale.order.is_subscription) attribue automatiquement le
    bon groupe de sécurité à l'utilisateur du client (account.move._post()).
    """

    @classmethod
    def setUpClass(cls):
        super().setUpClass()
        cls.standard_group = cls.env.ref('produits_tendance.group_trend_standard')
        cls.pro_group = cls.env.ref('produits_tendance.group_trend_pro')
        cls.monthly_plan = cls.env.ref('produits_tendance.subscription_plan_monthly')
        cls.pro_product = cls.env.ref('produits_tendance.product_tier_pro')
        cls.standard_product = cls.env.ref('produits_tendance.product_tier_standard')

        cls.user = cls.env['res.users'].create({
            'name': 'Client Test WIN-66',
            'login': 'win66.client@example.com',
        })

        # Une base fraîche n'a pas forcément de journal "vente" configuré
        # pour la société tant que le plan comptable de démo n'est pas
        # chargé (ce qui arrive APRÈS ce test lors de l'install) : account.move
        # ne peut alors pas deviner de journal via _search_default_journal().
        # On en crée un explicitement pour ne pas dépendre de cet ordre de
        # chargement.
        cls.sale_journal = cls.env['account.journal'].search([
            ('type', '=', 'sale'),
            ('company_id', '=', cls.env.company.id),
        ], limit=1)
        if not cls.sale_journal:
            cls.sale_journal = cls.env['account.journal'].create({
                'name': 'Test Sales Journal (WIN-66)',
                'type': 'sale',
                'code': 'TSJ66',
                'company_id': cls.env.company.id,
            })

        # Même raison : sans plan comptable chargé, aucun compte de produits
        # n'est disponible pour déterminer account_id sur les lignes de
        # facture (contrainte SQL account_move_line_check_accountable_required_fields).
        cls.income_account = cls.env['account.account'].create({
            'name': 'Test Income Account (WIN-66)',
            'code': 'TESTINC66',
            'account_type': 'income',
        })

        # Même raison encore : la ligne "à recevoir" générée automatiquement
        # par account.move (display_type='payment_term') a besoin du compte
        # client du partenaire (property_account_receivable_id), qui n'a pas
        # de valeur par défaut sans plan comptable chargé.
        cls.receivable_account = cls.env['account.account'].create({
            'name': 'Test Receivable Account (WIN-66)',
            'code': 'TESTREC66',
            'account_type': 'asset_receivable',
            'reconcile': True,
        })
        cls.user.partner_id.property_account_receivable_id = cls.receivable_account.id

    def _create_subscription_invoice(self, product):
        """Crée une commande d'abonnement minimale (plan_id fixé directement,
        sans passer par action_confirm() ni le workflow de paiement — notre
        hook ne dépend que de is_subscription, pas de l'état de la commande)
        puis une facture liée via sale_line_ids."""
        order = self.env['sale.order'].create({
            'partner_id': self.user.partner_id.id,
            'plan_id': self.monthly_plan.id,
        })
        order_line = self.env['sale.order.line'].create({
            'order_id': order.id,
            'product_id': product.product_variant_id.id,
            'product_uom_qty': 1,
        })
        self.assertTrue(order.is_subscription, "sanity check: la commande doit être reconnue comme abonnement")

        return self.env['account.move'].create({
            'move_type': 'out_invoice',
            'partner_id': self.user.partner_id.id,
            'journal_id': self.sale_journal.id,
            'invoice_line_ids': [(0, 0, {
                'product_id': product.product_variant_id.id,
                'quantity': 1,
                'price_unit': product.list_price,
                'account_id': self.income_account.id,
                'sale_line_ids': [(6, 0, [order_line.id])],
            })],
        })

    def test_invoice_validation_assigns_pro_group(self):
        invoice = self._create_subscription_invoice(self.pro_product)
        invoice.action_post()

        self.assertTrue(self.user.has_group('produits_tendance.group_trend_pro'))
        # implied_ids : Pro implique Standard.
        self.assertTrue(self.user.has_group('produits_tendance.group_trend_standard'))

    def test_invoice_validation_assigns_standard_group(self):
        invoice = self._create_subscription_invoice(self.standard_product)
        invoice.action_post()

        self.assertTrue(self.user.has_group('produits_tendance.group_trend_standard'))
        self.assertFalse(self.user.has_group('produits_tendance.group_trend_pro'))

    def test_upgrade_standard_to_pro_removes_standard_membership(self):
        self._create_subscription_invoice(self.standard_product).action_post()
        self.assertIn(self.standard_group, self.user.group_ids)

        self._create_subscription_invoice(self.pro_product).action_post()

        self.assertNotIn(self.standard_group, self.user.group_ids)
        self.assertIn(self.pro_group, self.user.group_ids)
        # L'accès Standard reste garanti via implied_ids, même sans membership explicite.
        self.assertTrue(self.user.has_group('produits_tendance.group_trend_standard'))

    def test_non_subscription_invoice_does_not_assign_group(self):
        invoice = self.env['account.move'].create({
            'move_type': 'out_invoice',
            'partner_id': self.user.partner_id.id,
            'journal_id': self.sale_journal.id,
            'invoice_line_ids': [(0, 0, {
                'name': 'Produit hors abonnement',
                'quantity': 1,
                'price_unit': 10.0,
                'account_id': self.income_account.id,
            })],
        })
        invoice.action_post()

        self.assertFalse(self.user.has_group('produits_tendance.group_trend_pro'))
        self.assertFalse(self.user.has_group('produits_tendance.group_trend_standard'))


class TestIsProUserGuard(TransactionCase):
    """WIN-66 : garde-fou réutilisable TrendDashboardAPI.is_pro_user()."""

    def test_is_pro_user_false_by_default(self):
        user = self.env['res.users'].create({'name': 'Guard Test', 'login': 'guard.test@example.com'})
        self.assertFalse(TrendDashboardAPI.is_pro_user(self.env(user=user)))

    def test_is_pro_user_true_when_in_group(self):
        pro_group = self.env.ref('produits_tendance.group_trend_pro')
        user = self.env['res.users'].create({
            'name': 'Guard Pro Test',
            'login': 'guard.pro.test@example.com',
            'group_ids': [(4, pro_group.id)],
        })
        self.assertTrue(TrendDashboardAPI.is_pro_user(self.env(user=user)))
