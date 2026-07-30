# models/account_move.py
"""WIN-66 : assignation automatique du groupe de sécurité à la validation
de la facture d'un abonnement (Tier Standard/Pro).

Point d'extension choisi : `account.move._post()`, confirmé être le hook
officiel utilisé par le module Enterprise `sale_subscription` lui-même pour
sa propre logique post-facturation (voir addons/sale_subscription/models/
account_move.py sur l'instance Odoo.sh) — donc le point le plus stable et le
moins risqué pour brancher notre propre logique, plutôt que de recréer notre
propre suivi des changements de `sale.order.subscription_state`.
"""
from odoo import models


class AccountMove(models.Model):
    _inherit = 'account.move'

    def _post(self, soft=True):
        posted = super()._post(soft=soft)
        posted._winners_assign_subscription_groups()
        return posted

    def _winners_assign_subscription_groups(self):
        """Pour chaque facture client validée liée à une commande
        d'abonnement (sale.order.is_subscription), attribue à l'utilisateur
        du client le groupe de sécurité rattaché à l'article acheté
        (product.template.winners_subscription_group_id).

        Si plusieurs tiers apparaissent (ex: upgrade Standard -> Pro sur la
        même commande), seul le plus élevé est conservé — les autres groupes
        de tier gérés par ce mécanisme sont retirés pour éviter qu'un client
        cumule plusieurs tiers.

        NB : ne gère pas la révocation lors d'une résiliation/churn d'abonnement
        (aucune nouvelle facture n'est alors validée) — hors périmètre du
        ticket WIN-66, qui ne couvre que le parcours d'achat.
        """
        tier_groups = (
            self.env.ref('produits_tendance.group_trend_standard')
            | self.env.ref('produits_tendance.group_trend_pro')
        )

        for move in self:
            if move.move_type != 'out_invoice' or move.state != 'posted':
                continue

            orders = move.line_ids.sale_line_ids.order_id.filtered('is_subscription')
            if not orders:
                continue

            products = orders.order_line.product_id.product_tmpl_id
            target_groups = products.mapped('winners_subscription_group_id')
            if not target_groups:
                continue

            # Ne garder que le(s) groupe(s) qui ne sont pas déjà impliqués par
            # un autre groupe ciblé (group_trend_pro implique déjà standard).
            highest_groups = target_groups.filtered(
                lambda g: g not in (target_groups - g).mapped('implied_ids')
            )

            users = move.partner_id.user_ids
            if not users:
                continue

            users.write({
                'group_ids': (
                    [(3, group.id) for group in (tier_groups - highest_groups)]
                    + [(4, group.id) for group in highest_groups]
                )
            })
