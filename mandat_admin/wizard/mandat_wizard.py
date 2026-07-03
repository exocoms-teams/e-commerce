# -*- coding: utf-8 -*-
import re
from odoo import api, fields, models, _
from odoo.exceptions import UserError, ValidationError


def luhn_ok(siret):
    s = re.sub(r'\s', '', siret)
    if not s.isdigit() or len(s) != 14:
        return False
    total = 0
    for i, d in enumerate(reversed(s)):
        n = int(d)
        if i % 2 == 1:
            n *= 2
            if n > 9:
                n -= 9
        total += n
    return total % 10 == 0


class MandatWizard(models.TransientModel):
    _name        = 'mandat.wizard'
    _description = 'Assistant Mandat Administratif – BCA complet'

    sale_order_id = fields.Many2one('sale.order', required=True, readonly=True)
    partner_id    = fields.Many2one(related='sale_order_id.partner_id', readonly=True)
    amount_total  = fields.Monetary(related='sale_order_id.amount_total', readonly=True)
    currency_id   = fields.Many2one(related='sale_order_id.currency_id', readonly=True)

    # Acheteur public
    acheteur_siret          = fields.Char('SIRET acheteur public *', size=14, required=True)
    acheteur_service        = fields.Char('Service / Direction *', required=True)
    acheteur_contact        = fields.Char('Nom du gestionnaire')
    nomenclature_budgetaire = fields.Selection([
        ('M14','M14'),('M57','M57'),('M22','M22'),
        ('M9','M9'),('M4','M4'),('M52','M52'),('M71','M71'),
    ], required=True, default='M14', string='Nomenclature *')

    # Engagement
    reference_bon_commande = fields.Char('Référence BCA organisme *', required=True)
    numero_engagement      = fields.Char('N° engagement juridique (EJ)')
    date_engagement        = fields.Date("Date d'engagement")
    numero_marche          = fields.Char('N° de marché public')
    objet_marche           = fields.Char('Objet du bon de commande *', required=True)

    # Imputation budgétaire
    section               = fields.Selection([
        ('fonctionnement', 'Fonctionnement'),
        ('investissement',  'Investissement'),
    ], required=True, default='fonctionnement', string='Section budgétaire *')
    chapitre              = fields.Char('Chapitre *', required=True)
    article               = fields.Char('Article *',  required=True)
    sous_article          = fields.Char('Sous-article')
    operation             = fields.Char('Opération / Fonction')
    exercice              = fields.Char('Exercice', default=lambda s: str(fields.Date.today().year))
    credit_ouvert         = fields.Monetary('Crédit ouvert',    currency_field='currency_id')
    disponible_budgetaire = fields.Monetary('Disponible',       currency_field='currency_id')
    visa_controleur       = fields.Char('Réf. visa contrôleur budgétaire')

    # Ordonnancement
    ordonnateur         = fields.Char('Ordonnateur *', required=True)
    qualite_ordonnateur = fields.Char("Qualité de l'ordonnateur *", required=True)
    comptable_public    = fields.Char('Comptable public assignataire *', required=True)

    # Chorus Pro
    structure_chorus  = fields.Char('Structure Chorus Pro (SIRET)')
    service_chorus    = fields.Char('Code service Chorus Pro')
    code_tiers_chorus = fields.Char('Code tiers Chorus Pro')

    # RIB fournisseur
    fournisseur_iban   = fields.Char('IBAN fournisseur *', required=True)
    fournisseur_bic    = fields.Char('BIC / SWIFT')
    fournisseur_banque = fields.Char('Banque')
    rib_certifie       = fields.Boolean("RIB certifié par l'ordonnateur *")

    # TVA publique
    regime_tva_public = fields.Selection([
        ('non_assujetti',     'Non assujetti'),
        ('assujetti_partiel', 'Assujetti partiel'),
        ('assujetti_total',   'Assujetti total'),
        ('fctva',             'FCTVA'),
    ], default='non_assujetti', string='Régime TVA')
    taux_fctva        = fields.Float('Taux FCTVA (%)', default=16.404)

    # Délais
    delai_paiement_jours   = fields.Integer('Délai paiement (jours)', default=30)
    taux_interet_moratoire = fields.Float('Taux IM (%)', default=3.5)
    indemnite_forfaitaire  = fields.Float('IFR (€)', default=40.0)

    note_mandat = fields.Text('Observations')
    generer_pj  = fields.Boolean('Générer la liste des PJ obligatoires standard', default=True)

    def _get_company_iban(self):
        bank = self.env['res.partner.bank'].sudo().search(
            [('partner_id', '=', self.env.company.partner_id.id)], limit=1
        )
        return bank.acc_number or ''

    @api.model
    def default_get(self, fields_list):
        res = super().default_get(fields_list)
        so_id = self.env.context.get('default_sale_order_id')
        if so_id:
            so = self.env['sale.order'].browse(so_id)
            p  = so.partner_id
            res.update({
                'acheteur_siret':          so.acheteur_siret or p.siret_public or '',
                'acheteur_service':        so.acheteur_service or p.service_public or '',
                'nomenclature_budgetaire': so.nomenclature_budgetaire or p.nomenclature_budgetaire or 'M14',
                'reference_bon_commande':  so.reference_bon_commande or '',
                'numero_engagement':       so.numero_engagement or '',
                'ordonnateur':             so.ordonnateur or '',
                'qualite_ordonnateur':     so.qualite_ordonnateur or '',
                'comptable_public':        so.comptable_public or p.comptable_public or '',
                'structure_chorus':        so.structure_chorus or p.structure_chorus or so.acheteur_siret or '',
                'service_chorus':          so.service_chorus or p.service_chorus or '',
                'code_tiers_chorus':       so.code_tiers_chorus or p.code_tiers_chorus or '',
                'regime_tva_public':       so.regime_tva_public or p.regime_tva_public or 'non_assujetti',
                'fournisseur_iban':        so.fournisseur_iban or self._get_company_iban(),
                'delai_paiement_jours':    so.delai_paiement_jours or 30,
                'note_mandat':             so.note_mandat or '',
            })
        return res

    def action_valider_bca(self):
        self.ensure_one()
        if not luhn_ok(self.acheteur_siret):
            raise ValidationError(
                _('SIRET invalide : %s (vérification Luhn échouée).') % self.acheteur_siret)
        iban = re.sub(r'\s', '', self.fournisseur_iban or '')
        if len(iban) < 15:
            raise ValidationError(_('IBAN invalide : %s') % self.fournisseur_iban)
        if not self.rib_certifie:
            raise UserError(_("Le RIB doit être certifié par l'ordonnateur avant émission du BCA."))

        so = self.sale_order_id
        vals = {
            'payment_mode':            'mandat_administratif',
            'acheteur_siret':          re.sub(r'\s', '', self.acheteur_siret),
            'acheteur_service':        self.acheteur_service,
            'acheteur_contact':        self.acheteur_contact,
            'nomenclature_budgetaire': self.nomenclature_budgetaire,
            'reference_bon_commande':  self.reference_bon_commande,
            'numero_engagement':       self.numero_engagement,
            'date_engagement':         self.date_engagement,
            'numero_marche':           self.numero_marche,
            'objet_marche':            self.objet_marche,
            'ordonnateur':             self.ordonnateur,
            'qualite_ordonnateur':     self.qualite_ordonnateur,
            'comptable_public':        self.comptable_public,
            'structure_chorus':        self.structure_chorus,
            'service_chorus':          self.service_chorus,
            'code_tiers_chorus':       self.code_tiers_chorus,
            'fournisseur_iban':        iban,
            'fournisseur_bic':         self.fournisseur_bic,
            'fournisseur_banque':      self.fournisseur_banque,
            'rib_certifie':            True,
            'regime_tva_public':       self.regime_tva_public,
            'taux_fctva':              self.taux_fctva,
            'delai_paiement_jours':    self.delai_paiement_jours,
            'taux_interet_moratoire':  self.taux_interet_moratoire,
            'indemnite_forfaitaire':   self.indemnite_forfaitaire,
            'note_mandat':             self.note_mandat,
            'mandat_state':            'bca_emis',
        }
        if not so.mandat_numero:
            vals['mandat_numero'] = so._gen_mandat_numero()
        so.write(vals)

        # Imputation budgétaire
        so.imputation_ids.unlink()
        self.env['mandat.imputation'].create({
            'sale_order_id':  so.id,
            'name':           '%s – %s' % (self.chapitre, self.article),
            'section':        self.section,
            'chapitre':       self.chapitre,
            'article':        self.article,
            'sous_article':   self.sous_article,
            'operation':      self.operation,
            'exercice':       self.exercice,
            'credit_ouvert':  self.credit_ouvert,
            'disponible':     self.disponible_budgetaire,
            'montant_engage': so.amount_total,
            'visa_controleur': self.visa_controleur,
            'currency_id':    so.currency_id.id,
        })

        # PJ standard
        if self.generer_pj:
            so.action_generer_pj_std()

        # Confirmation commande
        if so.state == 'draft':
            so.action_confirm()

        return {
            'type':      'ir.actions.act_window',
            'res_model': 'sale.order',
            'res_id':    so.id,
            'view_mode': 'form',
            'target':    'current',
        }

    def action_valider_et_imprimer(self):
        self.action_valider_bca()
        return self.sale_order_id.action_print_bca()
