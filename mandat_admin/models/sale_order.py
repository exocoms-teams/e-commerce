# -*- coding: utf-8 -*-
import re
from datetime import timedelta
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


class SaleOrder(models.Model):
    _inherit = 'sale.order'

    # ── Mode paiement ──────────────────────────────────────────────
    payment_mode = fields.Selection([
        ('mandat_administratif', '🏛 Mandat Administratif'),
    ], string='Mode de paiement', default=False)
    is_mandat_administratif = fields.Boolean(
        compute='_compute_is_ma', store=True, string='Est un mandat administratif')

    # ── Identification ─────────────────────────────────────────────
    mandat_numero = fields.Char('N° de mandat', copy=False, readonly=True, index=True)
    mandat_state = fields.Selection([
        ('draft',        'BCA en attente'),
        ('bca_emis',     'BCA émis'),
        ('service_fait', 'Service fait certifié'),
        ('pec',          'Prise en charge comptable'),
        ('mandate',      'Mandaté'),
        ('paye',         'Payé'),
        ('annule',       'Annulé'),
    ], default='draft', copy=False, tracking=True, string='État mandat')

    # ── Acheteur public ────────────────────────────────────────────
    acheteur_siret          = fields.Char('SIRET acheteur public', size=14)
    acheteur_service        = fields.Char('Service / Direction')
    acheteur_contact        = fields.Char('Nom du gestionnaire')
    nomenclature_budgetaire = fields.Selection([
        ('M14','M14'), ('M57','M57'), ('M22','M22'),
        ('M9','M9'), ('M4','M4'), ('M52','M52'), ('M71','M71'),
    ], default='M14', string='Nomenclature budgétaire')

    # ── Engagement ─────────────────────────────────────────────────
    reference_bon_commande = fields.Char('Référence BCA organisme')
    numero_engagement      = fields.Char('N° engagement juridique (EJ)')
    date_engagement        = fields.Date("Date d'engagement")
    numero_marche          = fields.Char('N° de marché public')
    objet_marche           = fields.Char('Objet du bon de commande')

    # ── Imputation budgétaire ──────────────────────────────────────
    imputation_ids = fields.One2many(
        'mandat.imputation', 'sale_order_id', 'Imputations budgétaires')

    # ── Ordonnancement ─────────────────────────────────────────────
    ordonnateur          = fields.Char('Ordonnateur')
    qualite_ordonnateur  = fields.Char("Qualité de l'ordonnateur")
    comptable_public     = fields.Char('Comptable public assignataire')
    code_tiers_chorus    = fields.Char('Code tiers Chorus Pro')
    structure_chorus     = fields.Char('Structure Chorus Pro')
    service_chorus       = fields.Char('Code service Chorus Pro')

    # ── Délais & intérêts moratoires ───────────────────────────────
    delai_paiement_jours       = fields.Integer('Délai paiement (j)', default=30)
    date_limite_paiement       = fields.Date('Date limite paiement',
                                              compute='_compute_dlp', store=True)
    taux_interet_moratoire     = fields.Float('Taux IM (%)', default=3.5)
    montant_interet_moratoire  = fields.Monetary('Intérêts moratoires',
                                                  compute='_compute_im', store=True,
                                                  currency_field='currency_id')
    indemnite_forfaitaire      = fields.Float('IFR (€)', default=40.0,
                                               help="Indemnité forfaitaire de recouvrement – art. L.2192-12 CCP")

    # ── RIB fournisseur ────────────────────────────────────────────
    fournisseur_iban   = fields.Char('IBAN fournisseur')
    fournisseur_bic    = fields.Char('BIC / SWIFT')
    fournisseur_banque = fields.Char('Banque fournisseur')
    rib_certifie       = fields.Boolean("RIB certifié par l'ordonnateur")

    # ── TVA publique ───────────────────────────────────────────────
    regime_tva_public = fields.Selection([
        ('non_assujetti',     'Non assujetti'),
        ('assujetti_partiel', 'Assujetti partiel'),
        ('assujetti_total',   'Assujetti total'),
        ('fctva',             'FCTVA'),
    ], default='non_assujetti', string='Régime TVA public')
    taux_fctva    = fields.Float('Taux FCTVA (%)', default=16.404)
    montant_fctva = fields.Monetary('Montant FCTVA',
                                     compute='_compute_fctva', store=True,
                                     currency_field='currency_id')

    # ── Service fait ───────────────────────────────────────────────
    service_fait_certifie      = fields.Boolean('Service fait certifié', copy=False)
    date_service_fait          = fields.Date('Date certification SF', copy=False)
    certificateur_service_fait = fields.Char('Certifié par', copy=False)
    reserve_service_fait       = fields.Text('Réserves', copy=False)

    # ── Prise en charge comptable ──────────────────────────────────
    pec_acceptee    = fields.Boolean('PEC acceptée', copy=False)
    date_pec        = fields.Date('Date PEC', copy=False)
    reference_pec   = fields.Char('Référence PEC', copy=False)
    motif_rejet_pec = fields.Text('Motif rejet PEC', copy=False)

    # ── Pièces justificatives ──────────────────────────────────────
    pj_ids       = fields.One2many('mandat.pj', 'sale_order_id', 'Pièces justificatives')
    pj_completes = fields.Boolean('PJ complètes', compute='_compute_pj', store=True)

    # ── Chorus Pro ─────────────────────────────────────────────────
    chorus_envoye      = fields.Boolean('Envoyé Chorus Pro', copy=False)
    date_envoi_chorus  = fields.Date('Date envoi Chorus', copy=False)
    numero_chorus      = fields.Char('N° dépôt Chorus', copy=False)
    statut_chorus      = fields.Selection([
        ('non_envoye', 'Non envoyé'), ('depose',   'Déposé'),
        ('en_cours',   'En cours'),   ('integre',  'Intégré'),
        ('rejete',     'Rejeté'),
    ], default='non_envoye', copy=False, string='Statut Chorus')

    note_mandat = fields.Text('Observations / Mentions particulières')

    # ── Computed ───────────────────────────────────────────────────

    @api.depends('payment_mode')
    def _compute_is_ma(self):
        for o in self:
            o.is_mandat_administratif = (o.payment_mode == 'mandat_administratif')

    @api.depends('date_order', 'delai_paiement_jours')
    def _compute_dlp(self):
        for o in self:
            if o.date_order and o.delai_paiement_jours:
                o.date_limite_paiement = (
                    o.date_order.date() + timedelta(days=o.delai_paiement_jours)
                )
            else:
                o.date_limite_paiement = False

    @api.depends('date_limite_paiement', 'mandat_state', 'amount_total', 'taux_interet_moratoire')
    def _compute_im(self):
        today = fields.Date.today()
        for o in self:
            if (o.date_limite_paiement
                    and o.mandat_state not in ('paye', 'annule')
                    and today > o.date_limite_paiement):
                jours = (today - o.date_limite_paiement).days
                o.montant_interet_moratoire = (
                    o.amount_total * (o.taux_interet_moratoire / 100) * jours / 365
                )
            else:
                o.montant_interet_moratoire = 0.0

    @api.depends('amount_tax', 'regime_tva_public', 'taux_fctva')
    def _compute_fctva(self):
        for o in self:
            o.montant_fctva = (
                o.amount_tax * (o.taux_fctva / 100)
                if o.regime_tva_public == 'fctva' else 0.0
            )

    @api.depends('pj_ids.obligatoire', 'pj_ids.fournie')
    def _compute_pj(self):
        for o in self:
            obl = o.pj_ids.filtered('obligatoire')
            o.pj_completes = bool(obl) and all(p.fournie for p in obl)

    # ── Contrainte SIRET ───────────────────────────────────────────

    @api.constrains('acheteur_siret')
    def _check_siret(self):
        for o in self:
            if o.acheteur_siret and not luhn_ok(o.acheteur_siret):
                raise ValidationError(
                    _('SIRET invalide : %s (vérification Luhn échouée).') % o.acheteur_siret
                )

    # ── Séquence ───────────────────────────────────────────────────

    def _gen_mandat_numero(self):
        self.ensure_one()
        seq = self.env['ir.sequence'].next_by_code('mandat.administratif') or '00001'
        return 'MA/%d/%s' % (fields.Date.today().year, seq)

    # ── Workflow ───────────────────────────────────────────────────

    def action_open_mandat_wizard(self):
        self.ensure_one()
        return {
            'type': 'ir.actions.act_window',
            'name': _('Mandat Administratif – BCA'),
            'res_model': 'mandat.wizard',
            'view_mode': 'form',
            'target': 'new',
            'context': {'default_sale_order_id': self.id},
        }

    def action_certifier_service_fait(self):
        self.ensure_one()
        if self.mandat_state != 'bca_emis':
            raise UserError(_('Le BCA doit être émis avant de certifier le service fait.'))
        return {
            'type': 'ir.actions.act_window',
            'name': _('Certification du service fait'),
            'res_model': 'service.fait.wizard',
            'view_mode': 'form',
            'target': 'new',
            'context': {'default_sale_order_id': self.id},
        }

    def action_prise_en_charge(self):
        self.ensure_one()
        if not self.service_fait_certifie:
            raise UserError(_("Certifiez d'abord le service fait."))
        return {
            'type': 'ir.actions.act_window',
            'name': _('Prise en charge comptable'),
            'res_model': 'pec.wizard',
            'view_mode': 'form',
            'target': 'new',
            'context': {'default_sale_order_id': self.id},
        }

    def action_mandater(self):
        self.ensure_one()
        if not self.pec_acceptee:
            raise UserError(_('La PEC doit être acceptée avant le mandatement.'))
        if not self.pj_completes:
            raise UserError(_('Toutes les pièces justificatives obligatoires doivent être fournies.'))
        self.mandat_state = 'mandate'

    def action_marquer_paye(self):
        self.mandat_state = 'paye'

    def action_annuler_mandat(self):
        self.mandat_state = 'annule'

    def action_generer_pj_std(self):
        """Génère la liste standard des PJ obligatoires."""
        self.ensure_one()
        types = [
            ('bon_commande',    'Bon de commande signé',             True),
            ('facture',         'Facture du fournisseur',             True),
            ('service_fait',    'Certification du service fait',      True),
            ('rib_fournisseur', 'RIB / IBAN du fournisseur certifié', True),
        ]
        if self.numero_marche:
            types += [
                ('marche_public',        "Acte d'engagement du marché",        True),
                ('pv_reception',         'PV de réception',                    False),
                ('attestation_fiscale',  'Attestation fiscale et sociale (DC7)', True),
            ]
        existing = self.pj_ids.mapped('type_pj')
        for tp, lib, obl in types:
            if tp not in existing:
                self.env['mandat.pj'].create({
                    'sale_order_id': self.id,
                    'type_pj': tp, 'libelle': lib, 'obligatoire': obl,
                })

    def action_print_bca(self):
        return self.env.ref('mandat_admin.report_bca').report_action(self)

    def action_export_facturx(self):
        """Génère un XML UBL 2.1 compatible Chorus Pro et propose le téléchargement."""
        self.ensure_one()
        xml_b64 = self._build_ubl_xml()
        att = self.env['ir.attachment'].create({
            'name': 'FacturX_%s.xml' % (self.mandat_numero or self.name),
            'type': 'binary', 'datas': xml_b64,
            'res_model': self._name, 'res_id': self.id,
            'mimetype': 'application/xml',
        })
        self.write({
            'statut_chorus':    'depose',
            'date_envoi_chorus': fields.Date.today(),
            'chorus_envoye':    True,
        })
        return {
            'type': 'ir.actions.act_url',
            'url': '/web/content/%d?download=true' % att.id,
            'target': 'self',
        }

    def _build_ubl_xml(self):
        import base64
        try:
            from lxml import etree
        except ImportError:
            return base64.b64encode(b'<Invoice/>').decode()

        NS = {
            None:  'urn:oasis:names:specification:ubl:schema:xsd:Invoice-2',
            'cac': 'urn:oasis:names:specification:ubl:schema:xsd:CommonAggregateComponents-2',
            'cbc': 'urn:oasis:names:specification:ubl:schema:xsd:CommonBasicComponents-2',
        }
        CBC = NS['cbc']; CAC = NS['cac']
        cbc = lambda t: '{%s}%s' % (CBC, t)
        cac = lambda t: '{%s}%s' % (CAC, t)

        root = etree.Element('Invoice', nsmap=NS)
        etree.SubElement(root, cbc('CustomizationID')).text = \
            'urn:cen.eu:en16931:2017#compliant#urn:fdc:peppol.eu:2017:poacc:billing:3.0'
        etree.SubElement(root, cbc('ProfileID')).text = \
            'urn:fdc:peppol.eu:2017:poacc:billing:01:1.0'
        etree.SubElement(root, cbc('ID')).text          = self.mandat_numero or self.name
        etree.SubElement(root, cbc('IssueDate')).text   = str(self.date_order.date()) if self.date_order else ''
        etree.SubElement(root, cbc('DueDate')).text     = str(self.date_limite_paiement) if self.date_limite_paiement else ''
        etree.SubElement(root, cbc('InvoiceTypeCode')).text = '380'
        etree.SubElement(root, cbc('DocumentCurrencyCode')).text = self.currency_id.name or 'EUR'
        if self.numero_engagement:
            etree.SubElement(root, cbc('BuyerReference')).text = self.numero_engagement
        if self.reference_bon_commande:
            po = etree.SubElement(root, cac('OrderReference'))
            etree.SubElement(po, cbc('ID')).text = self.reference_bon_commande

        # Fournisseur
        sup = etree.SubElement(root, cac('AccountingSupplierParty'))
        sp  = etree.SubElement(sup,  cac('Party'))
        sn  = etree.SubElement(sp,   cac('PartyName'))
        etree.SubElement(sn, cbc('Name')).text = self.company_id.name
        if self.company_id.vat:
            st = etree.SubElement(sp, cac('PartyTaxScheme'))
            etree.SubElement(st, cbc('CompanyID')).text = self.company_id.vat
            ts = etree.SubElement(st, cac('TaxScheme'))
            etree.SubElement(ts, cbc('ID')).text = 'VAT'

        # Acheteur
        cust = etree.SubElement(root, cac('AccountingCustomerParty'))
        cp   = etree.SubElement(cust, cac('Party'))
        cn   = etree.SubElement(cp,   cac('PartyName'))
        etree.SubElement(cn, cbc('Name')).text = self.partner_id.name
        if self.acheteur_siret:
            cl = etree.SubElement(cp, cac('PartyLegalEntity'))
            etree.SubElement(cl, cbc('CompanyID')).text = re.sub(r'\s', '', self.acheteur_siret)
        if self.structure_chorus:
            pid = etree.SubElement(cp, cac('PartyIdentification'))
            etree.SubElement(pid, cbc('ID'), schemeID='FR:SIRET').text = self.structure_chorus

        # Paiement SEPA
        if self.fournisseur_iban:
            pm = etree.SubElement(root, cac('PaymentMeans'))
            etree.SubElement(pm, cbc('PaymentMeansCode')).text = '30'
            fa = etree.SubElement(pm, cac('PayeeFinancialAccount'))
            etree.SubElement(fa, cbc('ID')).text = re.sub(r'\s', '', self.fournisseur_iban)
            if self.fournisseur_bic:
                fi = etree.SubElement(fa, cac('FinancialInstitutionBranch'))
                etree.SubElement(fi, cbc('ID')).text = self.fournisseur_bic

        # TVA
        tt = etree.SubElement(root, cac('TaxTotal'))
        etree.SubElement(tt, cbc('TaxAmount'),
                         currencyID=self.currency_id.name).text = str(round(self.amount_tax, 2))

        # Totaux
        lm = etree.SubElement(root, cac('LegalMonetaryTotal'))
        etree.SubElement(lm, cbc('LineExtensionAmount'), currencyID=self.currency_id.name).text = str(round(self.amount_untaxed, 2))
        etree.SubElement(lm, cbc('TaxExclusiveAmount'),  currencyID=self.currency_id.name).text = str(round(self.amount_untaxed, 2))
        etree.SubElement(lm, cbc('TaxInclusiveAmount'),  currencyID=self.currency_id.name).text = str(round(self.amount_total, 2))
        etree.SubElement(lm, cbc('PayableAmount'),       currencyID=self.currency_id.name).text = str(round(self.amount_total, 2))

        # Lignes
        for i, line in enumerate(self.order_line, 1):
            il = etree.SubElement(root, cac('InvoiceLine'))
            etree.SubElement(il, cbc('ID')).text = str(i)
            etree.SubElement(il, cbc('InvoicedQuantity'),
                             unitCode=line.product_uom.name or 'C62').text = str(line.product_uom_qty)
            etree.SubElement(il, cbc('LineExtensionAmount'),
                             currencyID=self.currency_id.name).text = str(round(line.price_subtotal, 2))
            itm = etree.SubElement(il, cac('Item'))
            etree.SubElement(itm, cbc('Name')).text = line.product_id.name or line.name or ''
            pr = etree.SubElement(il, cac('Price'))
            etree.SubElement(pr, cbc('PriceAmount'),
                             currencyID=self.currency_id.name).text = str(round(line.price_unit, 2))

        xml_bytes = etree.tostring(root, pretty_print=True, xml_declaration=True, encoding='UTF-8')
        return base64.b64encode(xml_bytes).decode()

    # ── Onchange ───────────────────────────────────────────────────

    @api.onchange('partner_id')
    def _onchange_partner_mandat(self):
        p = self.partner_id
        if p and p.is_organisme_public:
            self.payment_mode            = 'mandat_administratif'
            self.acheteur_siret          = p.siret_public or ''
            self.acheteur_service        = p.service_public or ''
            self.comptable_public        = p.comptable_public or ''
            self.nomenclature_budgetaire = p.nomenclature_budgetaire or 'M14'
            self.regime_tva_public       = p.regime_tva_public or 'non_assujetti'
            self.code_tiers_chorus       = p.code_tiers_chorus or ''
            self.structure_chorus        = p.structure_chorus or ''
            self.service_chorus          = p.service_chorus or ''
