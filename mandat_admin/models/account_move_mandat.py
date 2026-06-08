# -*- coding: utf-8 -*-
from odoo import models, fields, api, _
from odoo.exceptions import UserError


class AccountMove(models.Model):
    """
    Extension de account.move pour intégrer le journal "Mandat Administratif".

    Quand un paiement (account.payment) ou un règlement de facture utilise le
    journal dont le code est 'MAND', un mandat.administratif est créé
    automatiquement et lié à la facture concernée.

    Point d'entrée principal : _auto_create_mandat_if_needed(), appelé depuis :
      - account.payment : _synchronize_to_moves() → post hook via write()
      - account.move    : action_post() override ci-dessous
    """

    _inherit = 'account.move'

    # ── Lien vers le/les mandats créés depuis cette écriture ──────────────────
    mandat_ids = fields.One2many(
        comodel_name='mandat.administratif',
        inverse_name='invoice_id',
        string='Mandats administratifs',
        readonly=True,
        copy=False,
    )
    mandat_count = fields.Integer(
        string='Nb mandats',
        compute='_compute_mandat_count',
    )

    # ─────────────────────────────────────────────────────────────────────────
    # Calculs
    # ─────────────────────────────────────────────────────────────────────────

    @api.depends('mandat_ids')
    def _compute_mandat_count(self):
        for move in self:
            move.mandat_count = len(move.mandat_ids)

    # ─────────────────────────────────────────────────────────────────────────
    # Helpers
    # ─────────────────────────────────────────────────────────────────────────

    def _is_mandat_journal(self):
        """Retourne True si le journal de l'écriture est le journal mandat."""
        return self.journal_id.code == 'MAND'

    def _get_related_invoice(self):
        """
        Pour un paiement (payment_id défini) ou une écriture de règlement,
        retourne la facture fournisseur/client liée (account.move de type
        'in_invoice', 'out_invoice', etc.) s'il y en a une.
        """
        # Cas 1 : écriture issue d'un paiement → chercher via la réconciliation
        reconciled_lines = self.line_ids.filtered(
            lambda l: l.account_id.account_type in (
                'asset_receivable', 'liability_payable'
            )
        )
        invoices = self.env['account.move']
        for line in reconciled_lines:
            for matched in line.matched_debit_ids + line.matched_credit_ids:
                other_line = (
                    matched.debit_move_id
                    if matched.credit_move_id == line
                    else matched.credit_move_id
                )
                if other_line.move_id.is_invoice():
                    invoices |= other_line.move_id
        return invoices

    # ─────────────────────────────────────────────────────────────────────────
    # Création automatique du mandat
    # ─────────────────────────────────────────────────────────────────────────

    def _auto_create_mandat_if_needed(self):
        """
        Crée un mandat administratif pour chaque écriture utilisant le journal
        MAND, si aucun mandat n'existe déjà pour cette écriture.
        """
        MandatModel = self.env['mandat.administratif']
        for move in self:
            if not move._is_mandat_journal():
                continue
            if move.mandat_ids:
                # Un mandat existe déjà → ne pas dupliquer
                continue

            # ── Valeurs de base ──────────────────────────────────────────────
            partner = move.partner_id
            amount = abs(move.amount_total or move.amount_total_signed)
            currency = move.currency_id or self.env.ref('base.EUR')

            # Construire l'objet du mandat depuis la référence de l'écriture
            objet = move.name or move.ref or _('Paiement par mandat administratif')

            # ── Chercher la facture liée pour enrichir les données ────────────
            linked_invoices = move._get_related_invoice()
            first_invoice = linked_invoices[:1]
            if linked_invoices:
                first_inv = linked_invoices[:1]
                partner = partner or first_inv.partner_id
                amount = amount or abs(first_inv.amount_total)
                objet = first_inv.name or objet

            vals = {
                'objet': objet[:200],
                'montant_ht': amount,          # approximation ; peut être affiné
                'taux_tva': '0.0',             # pas de TVA sur un mandat
                'creancier_id': partner.id if partner else False,
                'ordonnateur_id': self.env.user.id,
                'collectivite_id': self.env.company.id,
                'piece_justificative': 'facture',
                'invoice_id': first_invoice.id if first_invoice else move.id,
                # Si une seule facture est liée, on stocke aussi sa référence
                'reference_creancier': (
                    linked_invoices[:1].name if linked_invoices else move.ref or ''
                ),
            }

            # creancier_id est requis → fallback sur le partenaire de la société
            if not vals.get('creancier_id'):
                vals['creancier_id'] = self.env.company.partner_id.id

            mandat = MandatModel.create(vals)
            mandat.message_post(
                body=_(
                    "Mandat créé automatiquement depuis l'écriture comptable "
                    "<b>%s</b> (journal : %s)."
                ) % (move.name or move.ref, move.journal_id.name)
            )

    # ─────────────────────────────────────────────────────────────────────────
    # Hooks ORM
    # ─────────────────────────────────────────────────────────────────────────

    def action_post(self):
        """
        Override de la validation de l'écriture comptable.
        Après la validation standard, on crée le mandat si le journal est MAND.
        """
        res = super().action_post()
        # On ne crée le mandat que sur les écritures validées (posted)
        posted = self.filtered(lambda m: m.state == 'posted')
        posted._auto_create_mandat_if_needed()
        return res

    # ─────────────────────────────────────────────────────────────────────────
    # Action vue mandat
    # ─────────────────────────────────────────────────────────────────────────

    def action_view_mandats(self):
        """Ouvrir les mandats liés à cette écriture depuis le bouton stat."""
        self.ensure_one()
        return {
            'type': 'ir.actions.act_window',
            'name': _('Mandats administratifs'),
            'res_model': 'mandat.administratif',
            'view_mode': 'list,form',
            'domain': [('invoice_id', '=', self.id)],
            'context': {
                'default_invoice_id': self.id,
                'default_creancier_id': self.partner_id.id,
                'default_montant_ht': abs(self.amount_total),
            },
        }


class AccountPayment(models.Model):
    """
    Extension de account.payment : détecter le journal mandat lors de la
    validation d'un paiement et déclencher la création du mandat sur
    l'écriture comptable associée.
    """

    _inherit = 'account.payment'

    def action_post(self):
        """
        Après validation du paiement, si le journal est MAND, on déclenche
        la création du mandat sur l'écriture générée.
        """
        res = super().action_post()
        for payment in self:
            if payment.journal_id.code == 'MAND' and payment.move_id:
                payment.move_id._auto_create_mandat_if_needed()
        return res
