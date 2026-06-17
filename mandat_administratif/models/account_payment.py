# -*- coding: utf-8 -*-
import re
from odoo import api, fields, models, _
from odoo.exceptions import UserError


class AccountPayment(models.Model):
    """
    Extension du formulaire de paiement Odoo 19.
    Lorsque l'agent sélectionne la méthode de paiement 'Mandat Administratif',
    un bloc de champs obligatoires s'affiche pour compléter le dossier
    conformément aux exigences de la comptabilité publique française (GBCP).
    """
    _inherit = 'account.payment'

    # Calculé à partir de la méthode de paiement sélectionnée
    is_mandat_administratif = fields.Boolean(
        'Paiement par mandat administratif',
        compute='_compute_is_ma',
        store=True,
    )

    # ── Lien vers les documents sources ───────────────────────────
    mandat_sale_order_id = fields.Many2one(
        'sale.order', 'Bon de Commande Administratif (BCA)',
        domain=[('is_mandat_administratif', '=', True),
                ('mandat_state', 'not in', ['annule', 'paye'])],
        copy=False,
        help="Sélectionnez le BCA source pour pré-remplir automatiquement les champs du mandat.",
    )
    mandat_invoice_id = fields.Many2one(
        'account.move', 'Facture liée au mandat',
        domain=[('is_mandat_administratif', '=', True),
                ('move_type', '=', 'out_invoice')],
        copy=False,
    )

    # ── Identification du mandat ───────────────────────────────────
    mandat_numero           = fields.Char('N° de mandat')
    numero_engagement       = fields.Char('N° engagement juridique (EJ)')
    reference_bon_commande  = fields.Char('Référence BCA organisme')
    acheteur_siret          = fields.Char('SIRET acheteur public')

    # ── Ordonnancement ─────────────────────────────────────────────
    ordonnateur          = fields.Char('Ordonnateur')
    qualite_ordonnateur  = fields.Char("Qualité de l'ordonnateur")
    comptable_public     = fields.Char('Comptable public assignataire')
    date_mandatement     = fields.Date('Date de mandatement', default=fields.Date.today)
    reference_bordereau  = fields.Char('Référence du bordereau')

    # ── RIB / virement SEPA ────────────────────────────────────────
    fournisseur_iban   = fields.Char('IBAN fournisseur')
    fournisseur_bic    = fields.Char('BIC / SWIFT')
    fournisseur_banque = fields.Char('Banque fournisseur')
    rib_certifie       = fields.Boolean("RIB certifié par l'ordonnateur")

    # ── Imputation budgétaire ──────────────────────────────────────
    imputation_ids = fields.One2many(
        'mandat.imputation', 'payment_id', 'Imputations budgétaires')

    # ── Pièces justificatives ──────────────────────────────────────
    pj_ids = fields.One2many(
        'mandat.pj', 'payment_id', 'Pièces justificatives')

    # ── Service fait ───────────────────────────────────────────────
    service_fait_certifie = fields.Boolean('Service fait certifié')
    date_service_fait     = fields.Date('Date du service fait')
    certificateur_sf      = fields.Char('Certifié par')

    # ── Chorus Pro ─────────────────────────────────────────────────
    structure_chorus = fields.Char('Structure Chorus Pro')
    service_chorus   = fields.Char('Code service Chorus Pro')
    statut_chorus    = fields.Selection([
        ('non_envoye', 'Non envoyé'), ('depose',  'Déposé'),
        ('en_cours',   'En cours'),   ('integre', 'Intégré'),
        ('rejete',     'Rejeté'),
    ], default='non_envoye', copy=False)
    numero_chorus = fields.Char('N° dépôt Chorus', copy=False)

    # ── Intérêts moratoires éventuels ─────────────────────────────
    montant_interet_moratoire = fields.Monetary(
        'Intérêts moratoires éventuels', currency_field='currency_id')

    note_mandat = fields.Text('Observations / Mentions particulières')

    # ── Computed ───────────────────────────────────────────────────

    @api.depends('payment_method_id', 'payment_method_line_id')
    def _compute_is_ma(self):
        for pay in self:
            code = ''
            if pay.payment_method_id:
                code = pay.payment_method_id.code or ''
            elif pay.payment_method_line_id and pay.payment_method_line_id.payment_method_id:
                code = pay.payment_method_line_id.payment_method_id.code or ''
            pay.is_mandat_administratif = (code == 'mandat_administratif')

    # ── Onchange : auto-remplissage depuis le BCA ──────────────────

    @api.onchange('mandat_sale_order_id')
    def _onchange_bca(self):
        so = self.mandat_sale_order_id
        if not so:
            return
        self.mandat_numero           = so.mandat_numero
        self.numero_engagement       = so.numero_engagement
        self.reference_bon_commande  = so.reference_bon_commande
        self.acheteur_siret          = so.acheteur_siret
        self.ordonnateur             = so.ordonnateur
        self.qualite_ordonnateur     = so.qualite_ordonnateur
        self.comptable_public        = so.comptable_public
        self.fournisseur_iban        = so.fournisseur_iban
        self.fournisseur_bic         = so.fournisseur_bic
        self.fournisseur_banque      = so.fournisseur_banque
        self.rib_certifie            = so.rib_certifie
        self.structure_chorus        = so.structure_chorus
        self.service_chorus          = so.service_chorus
        self.service_fait_certifie   = so.service_fait_certifie
        self.date_service_fait       = so.date_service_fait
        self.certificateur_sf        = so.certificateur_service_fait
        self.montant_interet_moratoire = so.montant_interet_moratoire
        # Reprendre les imputations
        if so.imputation_ids and not self.imputation_ids:
            lines = [(0, 0, {
                'name':           imp.name,
                'section':        imp.section,
                'chapitre':       imp.chapitre,
                'article':        imp.article,
                'sous_article':   imp.sous_article,
                'operation':      imp.operation,
                'exercice':       imp.exercice,
                'montant_engage': imp.montant_engage,
                'montant_mandate': imp.montant_engage,
                'currency_id':    imp.currency_id.id,
            }) for imp in so.imputation_ids]
            self.imputation_ids = lines

    @api.onchange('mandat_invoice_id')
    def _onchange_invoice_ma(self):
        inv = self.mandat_invoice_id
        if inv and not self.mandat_sale_order_id:
            self.mandat_numero           = inv.mandat_numero
            self.numero_engagement       = inv.numero_engagement
            self.acheteur_siret          = inv.acheteur_siret
            self.ordonnateur             = inv.ordonnateur
            self.qualite_ordonnateur     = inv.qualite_ordonnateur
            self.comptable_public        = inv.comptable_public

    # ── Validation avant paiement ──────────────────────────────────

    def action_post(self):
        for pay in self:
            if pay.is_mandat_administratif:
                errors = []
                if not pay.mandat_numero:
                    errors.append(_('• Le numéro de mandat est obligatoire.'))
                if not pay.ordonnateur:
                    errors.append(_("• L'ordonnateur doit être renseigné."))
                if not pay.comptable_public:
                    errors.append(_('• Le comptable public assignataire est obligatoire.'))
                if not pay.fournisseur_iban:
                    errors.append(_("• L'IBAN du fournisseur est obligatoire pour le virement SEPA."))
                if not pay.rib_certifie:
                    errors.append(_("• Le RIB doit être certifié par l'ordonnateur."))
                if not pay.service_fait_certifie:
                    errors.append(_('• La certification du service fait est obligatoire.'))
                if errors:
                    raise UserError(
                        _('Impossible de valider le paiement par mandat administratif :\n\n')
                        + '\n'.join(errors)
                    )
                # Mise à jour de l'état de la commande source
                if (pay.mandat_sale_order_id
                        and pay.mandat_sale_order_id.mandat_state == 'mandate'):
                    pay.mandat_sale_order_id.action_marquer_paye()
        return super().action_post()


class AccountPaymentMethod(models.Model):
    _inherit = 'account.payment.method'

    @api.model
    def _get_payment_method_information(self):
        res = super()._get_payment_method_information()
        res['mandat_administratif'] = {
            'mode':   'unique',
            'domain': [('type', '=', 'receivable')],
        }
        return res
