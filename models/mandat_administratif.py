# -*- coding: utf-8 -*-
from odoo import api, fields, models, _
from odoo.exceptions import UserError, ValidationError
from datetime import date


class MandatAdministratif(models.Model):
    _name = 'mandat.administratif'
    _description = 'Mandat Administratif'
    _inherit = ['mail.thread', 'mail.activity.mixin']
    _order = 'name desc'
    _rec_name = 'name'

    # ─── Identification ────────────────────────────────────────────────────────
    name = fields.Char(
        string='Numéro de mandat',
        readonly=True,
        default='/',
        copy=False,
        tracking=True,
    )
    reference_objet = fields.Char(
        string='Objet du mandat',
        required=True,
        tracking=True,
    )
    date_mandat = fields.Date(
        string='Date du mandat',
        default=fields.Date.today,
        required=True,
        tracking=True,
    )
    date_echeance = fields.Date(
        string="Date d'échéance",
        tracking=True,
    )

    # ─── Parties ───────────────────────────────────────────────────────────────
    ordonnateur_id = fields.Many2one(
        'res.partner',
        string='Ordonnateur',
        required=True,
        tracking=True,
        help="L'ordonnateur est l'agent habilité à prescrire l'exécution des dépenses.",
    )
    comptable_id = fields.Many2one(
        'res.partner',
        string='Comptable public assignataire',
        required=True,
        tracking=True,
        help="Le comptable public chargé du paiement du mandat.",
    )
    creancier_id = fields.Many2one(
        'res.partner',
        string='Créancier',
        required=True,
        tracking=True,
        domain="[('is_company', 'in', [True, False])]",
    )

    # ─── Références comptables ─────────────────────────────────────────────────
    imputation_budgetaire = fields.Char(
        string='Imputation budgétaire',
        required=True,
        tracking=True,
        help="Chapitre, article, paragraphe budgétaire (ex: 011-6064).",
    )
    engagement_id = fields.Many2one(
        'engagement.budgetaire',
        string='Engagement budgétaire',
        tracking=True,
        ondelete='restrict',
    )
    exercice_budgetaire = fields.Integer(
        string='Exercice budgétaire',
        default=lambda self: date.today().year,
        required=True,
    )
    bordereau_id = fields.Many2one(
        'bordereau.mandat',
        string='Bordereau de mandats',
        readonly=True,
        tracking=True,
    )

    # ─── Montants ──────────────────────────────────────────────────────────────
    currency_id = fields.Many2one(
        'res.currency',
        string='Devise',
        default=lambda self: self.env.company.currency_id,
        required=True,
    )
    montant_ht = fields.Monetary(
        string='Montant HT',
        currency_field='currency_id',
        required=True,
        tracking=True,
    )
    montant_tva = fields.Monetary(
        string='Montant TVA',
        currency_field='currency_id',
        compute='_compute_montants',
        store=True,
    )
    montant_ttc = fields.Monetary(
        string='Montant TTC',
        currency_field='currency_id',
        compute='_compute_montants',
        store=True,
        tracking=True,
    )
    taux_tva = fields.Selection(
        [('0', '0%'), ('5.5', '5,5%'), ('10', '10%'), ('20', '20%')],
        string='Taux TVA',
        default='20',
        required=True,
    )
    retenue_garantie = fields.Monetary(
        string='Retenue de garantie',
        currency_field='currency_id',
        default=0.0,
    )
    montant_net_payer = fields.Monetary(
        string='Montant net à payer',
        currency_field='currency_id',
        compute='_compute_montants',
        store=True,
        tracking=True,
    )

    # ─── Documents justificatifs ───────────────────────────────────────────────
    invoice_id = fields.Many2one(
        'account.move',
        string='Facture liée',
        domain="[('move_type', 'in', ['in_invoice', 'in_refund'])]",
        tracking=True,
    )
    purchase_order_id = fields.Many2one(
        'purchase.order',
        string='Bon de commande',
        tracking=True,
    )
    numero_marche = fields.Char(
        string='Numéro de marché',
        tracking=True,
    )
    piece_jointe_ids = fields.Many2many(
        'ir.attachment',
        'mandat_attachment_rel',
        'mandat_id',
        'attachment_id',
        string='Pièces justificatives',
    )

    # ─── Paiement ──────────────────────────────────────────────────────────────
    mode_paiement = fields.Selection(
        [
            ('virement', 'Virement bancaire'),
            ('cheque', 'Chèque'),
            ('numeraire', 'Numéraire'),
            ('prelevement', 'Prélèvement'),
        ],
        string='Mode de paiement',
        default='virement',
        required=True,
    )
    iban_creancier = fields.Char(
        string='IBAN créancier',
        related='creancier_id.bank_ids.acc_number',
        readonly=True,
    )
    date_paiement = fields.Date(
        string='Date de paiement',
        readonly=True,
        tracking=True,
    )
    journal_id = fields.Many2one(
        'account.journal',
        string='Journal de paiement',
        domain="[('type', 'in', ['bank', 'cash'])]",
    )

    # ─── Workflow & État ───────────────────────────────────────────────────────
    state = fields.Selection(
        [
            ('brouillon', 'Brouillon'),
            ('liquidation', 'En liquidation'),
            ('ordonnancement', 'Ordonnancé'),
            ('prise_en_charge', 'Pris en charge'),
            ('paye', 'Payé'),
            ('rejete', 'Rejeté'),
            ('annule', 'Annulé'),
        ],
        string='État',
        default='brouillon',
        tracking=True,
        copy=False,
    )
    motif_rejet = fields.Text(
        string='Motif de rejet',
        tracking=True,
    )

    # ─── Dates workflow ────────────────────────────────────────────────────────
    date_liquidation = fields.Date(string='Date de liquidation', readonly=True)
    date_ordonnancement = fields.Date(string="Date d'ordonnancement", readonly=True)
    date_prise_en_charge = fields.Date(string='Date de prise en charge', readonly=True)

    # ─── Utilisateurs ──────────────────────────────────────────────────────────
    user_liquidateur_id = fields.Many2one('res.users', string='Liquidateur', readonly=True)
    user_ordonnateur_id = fields.Many2one('res.users', string='Validateur', readonly=True)
    user_comptable_id = fields.Many2one('res.users', string='Comptable', readonly=True)

    # ─── Notes ─────────────────────────────────────────────────────────────────
    notes = fields.Html(string='Notes internes')
    company_id = fields.Many2one(
        'res.company',
        string='Société',
        default=lambda self: self.env.company,
        required=True,
    )

    # ─── Champs calculés ───────────────────────────────────────────────────────
    is_late = fields.Boolean(
        string='En retard',
        compute='_compute_is_late',
    )
    days_overdue = fields.Integer(
        string='Jours de retard',
        compute='_compute_is_late',
    )

    # ═══════════════════════════════════════════════════════════════════════════
    # COMPUTE
    # ═══════════════════════════════════════════════════════════════════════════

    @api.depends('montant_ht', 'taux_tva', 'retenue_garantie')
    def _compute_montants(self):
        for rec in self:
            taux = float(rec.taux_tva or '0') / 100
            rec.montant_tva = rec.montant_ht * taux
            rec.montant_ttc = rec.montant_ht + rec.montant_tva
            rec.montant_net_payer = rec.montant_ttc - rec.retenue_garantie

    @api.depends('date_echeance', 'state')
    def _compute_is_late(self):
        today = date.today()
        for rec in self:
            if rec.date_echeance and rec.state not in ('paye', 'annule', 'rejete'):
                delta = (today - rec.date_echeance).days
                rec.is_late = delta > 0
                rec.days_overdue = max(0, delta)
            else:
                rec.is_late = False
                rec.days_overdue = 0

    # ═══════════════════════════════════════════════════════════════════════════
    # ONCHANGE
    # ═══════════════════════════════════════════════════════════════════════════

    @api.onchange('invoice_id')
    def _onchange_invoice_id(self):
        if self.invoice_id:
            inv = self.invoice_id
            self.creancier_id = inv.partner_id
            self.montant_ht = inv.amount_untaxed
            self.montant_tva = inv.amount_tax
            self.purchase_order_id = inv.purchase_order_ids[:1] if hasattr(inv, 'purchase_order_ids') else False

    @api.onchange('purchase_order_id')
    def _onchange_purchase_order_id(self):
        if self.purchase_order_id:
            po = self.purchase_order_id
            self.creancier_id = po.partner_id
            self.numero_marche = po.name

    # ═══════════════════════════════════════════════════════════════════════════
    # ACTIONS WORKFLOW
    # ═══════════════════════════════════════════════════════════════════════════

    def action_mettre_en_liquidation(self):
        """Phase 1 : Liquidation - vérification du service fait"""
        self.ensure_one()
        self._check_mandat_complet()
        self.write({
            'state': 'liquidation',
            'date_liquidation': date.today(),
            'user_liquidateur_id': self.env.uid,
        })
        self.message_post(
            body=_("Mandat mis en phase de <b>liquidation</b> par %s.") % self.env.user.name,
            subtype_xmlid='mail.mt_note',
        )

    def action_ordonnancer(self):
        """Phase 2 : Ordonnancement - émission du mandat par l'ordonnateur"""
        self.ensure_one()
        if self.state != 'liquidation':
            raise UserError(_("Le mandat doit être en phase de liquidation pour être ordonnancé."))
        if self.name == '/':
            self.name = self.env['ir.sequence'].next_by_code('mandat.administratif') or '/'
        self.write({
            'state': 'ordonnancement',
            'date_ordonnancement': date.today(),
            'user_ordonnateur_id': self.env.uid,
        })
        self.message_post(
            body=_("Mandat <b>ordonnancé</b> (n° %s) par %s.") % (self.name, self.env.user.name),
            subtype_xmlid='mail.mt_note',
        )

    def action_prendre_en_charge(self):
        """Phase 3 : Prise en charge par le comptable public"""
        self.ensure_one()
        if self.state != 'ordonnancement':
            raise UserError(_("Le mandat doit être ordonnancé avant la prise en charge."))
        self.write({
            'state': 'prise_en_charge',
            'date_prise_en_charge': date.today(),
            'user_comptable_id': self.env.uid,
        })
        self.message_post(
            body=_("Mandat <b>pris en charge</b> par le comptable %s.") % self.env.user.name,
            subtype_xmlid='mail.mt_note',
        )

    def action_payer(self):
        """Phase 4 : Paiement effectif"""
        self.ensure_one()
        if self.state != 'prise_en_charge':
            raise UserError(_("Le mandat doit être pris en charge avant d'être payé."))
        self.write({
            'state': 'paye',
            'date_paiement': date.today(),
        })
        # Mise à jour de l'engagement budgétaire
        if self.engagement_id:
            self.engagement_id._update_consomme(self.montant_net_payer)
        self.message_post(
            body=_("Mandat <b>payé</b> le %s. Montant : %s %s.") % (
                date.today().strftime('%d/%m/%Y'),
                self.montant_net_payer,
                self.currency_id.symbol,
            ),
            subtype_xmlid='mail.mt_note',
        )

    def action_rejeter(self):
        """Rejet du mandat par le comptable"""
        self.ensure_one()
        return {
            'type': 'ir.actions.act_window',
            'name': _('Motif de rejet'),
            'res_model': 'wizard.rejeter.mandat',
            'view_mode': 'form',
            'target': 'new',
            'context': {'default_mandat_id': self.id},
        }

    def action_annuler(self):
        """Annulation du mandat"""
        self.ensure_one()
        if self.state == 'paye':
            raise UserError(_("Impossible d'annuler un mandat déjà payé."))
        self.write({'state': 'annule'})
        self.message_post(
            body=_("Mandat <b>annulé</b> par %s.") % self.env.user.name,
            subtype_xmlid='mail.mt_note',
        )

    def action_remettre_brouillon(self):
        """Remettre en brouillon (ex : mandat rejeté)"""
        self.ensure_one()
        if self.state not in ('rejete', 'annule', 'liquidation'):
            raise UserError(_("Impossible de remettre ce mandat en brouillon dans son état actuel."))
        self.write({'state': 'brouillon', 'motif_rejet': False})

    # ═══════════════════════════════════════════════════════════════════════════
    # VALIDATIONS
    # ═══════════════════════════════════════════════════════════════════════════

    def _check_mandat_complet(self):
        """Vérifie que le mandat est complet avant liquidation"""
        errors = []
        if not self.creancier_id:
            errors.append(_("Le créancier est obligatoire."))
        if not self.montant_ht or self.montant_ht <= 0:
            errors.append(_("Le montant HT doit être positif."))
        if not self.imputation_budgetaire:
            errors.append(_("L'imputation budgétaire est obligatoire."))
        if errors:
            raise ValidationError('\n'.join(errors))

    @api.constrains('montant_ht', 'retenue_garantie')
    def _check_montants(self):
        for rec in self:
            if rec.montant_ht < 0:
                raise ValidationError(_("Le montant HT ne peut pas être négatif."))
            if rec.retenue_garantie < 0:
                raise ValidationError(_("La retenue de garantie ne peut pas être négative."))
            if rec.retenue_garantie > rec.montant_ttc:
                raise ValidationError(_("La retenue de garantie ne peut pas dépasser le montant TTC."))

    # ═══════════════════════════════════════════════════════════════════════════
    # CRUD
    # ═══════════════════════════════════════════════════════════════════════════

    @api.model_create_multi
    def create(self, vals_list):
        for vals in vals_list:
            if vals.get('name', '/') == '/':
                # Le numéro sera attribué à l'ordonnancement
                vals['name'] = '/'
        return super().create(vals_list)

    def unlink(self):
        for rec in self:
            if rec.state not in ('brouillon', 'annule'):
                raise UserError(_(
                    "Impossible de supprimer le mandat %s. "
                    "Seuls les mandats en brouillon ou annulés peuvent être supprimés."
                ) % rec.name)
        return super().unlink()

    # ═══════════════════════════════════════════════════════════════════════════
    # ACTIONS UI
    # ═══════════════════════════════════════════════════════════════════════════

    def action_voir_facture(self):
        self.ensure_one()
        if not self.invoice_id:
            raise UserError(_("Aucune facture liée à ce mandat."))
        return {
            'type': 'ir.actions.act_window',
            'res_model': 'account.move',
            'res_id': self.invoice_id.id,
            'view_mode': 'form',
        }

    def action_imprimer_mandat(self):
        return self.env.ref('mandat_administratif.action_report_mandat_administratif').report_action(self)

    def action_imprimer_bordereau(self):
        if not self.bordereau_id:
            raise UserError(_("Ce mandat n'est pas rattaché à un bordereau."))
        return self.env.ref('mandat_administratif.action_report_bordereau_mandats').report_action(self.bordereau_id)
