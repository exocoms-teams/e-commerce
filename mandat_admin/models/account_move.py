# -*- coding: utf-8 -*-
import base64
import logging
import re

from odoo import _, api, fields, models
from odoo.exceptions import UserError

_logger = logging.getLogger(__name__)

CHORUS_PRO_URL = "https://portail.chorus-pro.gouv.fr"

FLUX_SYNTAXES = {
    'facturx': 'IN_DP_E2_FACTURX',
    'cii': 'IN_DP_E1_CII_16B',
    'ubl': 'IN_DP_E1_UBL_INVOICE',
}


class AccountMove(models.Model):
    _inherit = 'account.move'

    is_mandat_administratif = fields.Boolean(
        'Facture sous mandat administratif', default=False, copy=False)
    mandat_numero           = fields.Char('N° de mandat', copy=False)
    mandat_sale_order_id    = fields.Many2one(
        'sale.order', 'BCA source', copy=False,
        domain=[('is_mandat_administratif', '=', True)])

    # Champs engagement repris du BCA
    numero_engagement       = fields.Char('N° engagement juridique')
    acheteur_siret          = fields.Char('SIRET acheteur public')
    reference_bon_commande  = fields.Char('Référence BCA organisme')
    ordonnateur             = fields.Char('Ordonnateur')
    qualite_ordonnateur     = fields.Char("Qualité de l'ordonnateur")
    comptable_public        = fields.Char('Comptable public assignataire')
    structure_chorus        = fields.Char('Structure Chorus Pro')
    service_chorus          = fields.Char('Code service Chorus Pro')

    # Dates
    date_mandatement = fields.Date('Date de mandatement', copy=False)
    date_pec         = fields.Date('Date de prise en charge', copy=False)

    # Service fait
    service_fait_certifie = fields.Boolean('Service fait certifié', copy=False)
    date_service_fait     = fields.Date('Date du service fait', copy=False)
    certificateur_sf      = fields.Char('Certifié par', copy=False)

    # Sous-objets
    imputation_ids = fields.One2many(
        'mandat.imputation', 'invoice_id', 'Imputations budgétaires')
    pj_ids = fields.One2many(
        'mandat.pj', 'invoice_id', 'Pièces justificatives')

    # Chorus
    statut_chorus = fields.Selection([
        ('non_envoye', 'Non envoyé'), ('depose',  'Déposé'),
        ('en_cours',   'En cours'),   ('integre', 'Intégré'),
        ('rejete',     'Rejeté'),
    ], default='non_envoye', copy=False)
    numero_chorus      = fields.Char('N° dépôt Chorus', copy=False)
    chorus_sent_date   = fields.Datetime('Date de dépôt Chorus Pro', copy=False)

    engagement_juridique = fields.Char(
        string="N° d'engagement juridique",
        copy=False,
        help="Numéro d'engagement juridique requis par Chorus Pro (BT-13 EN 16931).",
    )
    chorus_flux_number = fields.Char(
        string="N° de flux Chorus Pro",
        copy=False, readonly=True,
    )
    chorus_flux_status = fields.Char(
        string="Statut du flux Chorus Pro",
        copy=False, readonly=True,
    )

    # Bordereaux
    bordereau_ids = fields.Many2many(
        'mandat.bordereau',
        'bordereau_invoice_rel', 'invoice_id', 'bordereau_id',
        string='Bordereaux')

    def action_mark_chorus_sent(self):
        for move in self:
            move.write({
                'statut_chorus': 'depose',
                'chorus_sent_date': fields.Datetime.now(),
            })
            move.message_post(
                body=_("Facture déposée sur Chorus Pro le %s.",
                       fields.Datetime.now().strftime('%d/%m/%Y %H:%M')),
            )

    def action_reset_chorus_sent(self):
        self.write({'statut_chorus': 'non_envoye', 'chorus_sent_date': False})

    def action_open_chorus_pro(self):
        return {'type': 'ir.actions.act_url', 'url': CHORUS_PRO_URL, 'target': 'new'}

    def _chorus_get_flux_file(self):
        self.ensure_one()
        syntax = self.company_id.chorus_flux_syntax or 'facturx'
        stamp = fields.Datetime.now().strftime('%Y%m%d%H%M%S')
        base_name = "%s_%s" % (
            re.sub(r'[^A-Za-z0-9_-]', '_', self.name or 'FACTURE'), stamp)
        if syntax == 'facturx':
            attachment = self.invoice_pdf_report_id
            if not attachment or not attachment.raw:
                raise UserError(_(
                    "Aucun PDF Factur-X généré pour %s. Imprimez d'abord la facture.",
                    self.display_name))
            return f"{base_name}.pdf", attachment.raw
        builder_model = 'account.edi.xml.cii' if syntax == 'cii' else 'account.edi.xml.ubl_21'
        builder = self.env[builder_model]
        result = builder._export_invoice(self)
        content, errors = result if isinstance(result, (tuple, list)) else (result, None)
        if errors:
            raise UserError(_("Erreurs XML %(s)s : %(e)s", s=syntax.upper(), e="\n".join(str(e) for e in errors)))
        if isinstance(content, str):
            content = content.encode('utf-8')
        return f"{base_name}.xml", content

    def action_send_to_chorus(self):
        for move in self:
            company = move.company_id
            if not company.chorus_api_active:
                raise UserError(_("L'envoi automatique Chorus Pro n'est pas activé.\nComptabilité → Configuration → Paramètres → Chorus Pro."))
            if move.move_type not in ('out_invoice', 'out_refund'):
                raise UserError(_("Seules les factures et avoirs clients peuvent être déposés sur Chorus Pro."))
            if move.state != 'posted':
                raise UserError(_("La facture %s doit être comptabilisée avant l'envoi.", move.display_name))
            partner = move.partner_id.commercial_partner_id
            if not partner.is_organisme_public:
                raise UserError(_("Le client %s n'est pas un organisme public.", partner.name))
            if partner.chorus_engagement_required and not move.engagement_juridique:
                raise UserError(_("Cette structure exige un n° d'engagement juridique sur la facture %s.", move.display_name))
            filename, content = move._chorus_get_flux_file()
            syntax_code = FLUX_SYNTAXES[company.chorus_flux_syntax or 'facturx']
            result = company._chorus_request(
                '/cpro/factures/v1/deposer/flux',
                {'fichierFlux': base64.b64encode(content).decode(), 'nomFichier': filename, 'syntaxeFlux': syntax_code, 'avecSignature': False},
            )
            flux_number = result.get('numeroFluxDepot')
            move.write({'chorus_sent': True, 'chorus_sent_date': fields.Datetime.now(), 'chorus_flux_number': flux_number, 'chorus_flux_status': _("Déposé — en cours de traitement")})
            move.message_post(body=_("Facture déposée sur Chorus Pro via l'API PISTE.<br/>Fichier : %(f)s — N° de flux : <b>%(n)s</b>", f=filename, n=flux_number or _("non communiqué")))
        return True

    def action_check_chorus_status(self):
        for move in self:
            if not move.chorus_flux_number:
                raise UserError(_("Aucun numéro de flux Chorus Pro sur %s.", move.display_name))
            result = move.company_id._chorus_request('/cpro/transverses/v1/consulterCR', {'numeroFluxDepot': move.chorus_flux_number})
            status = result.get('etatCourantFlux') or result.get('statutFlux') or result.get('libelle') or _("statut inconnu")
            move.chorus_flux_status = status
            move.message_post(body=_("Statut flux Chorus Pro %(f)s : <b>%(s)s</b>", f=move.chorus_flux_number, s=status))
        return True

    @api.model
    def _cron_check_chorus_status(self):
        moves = self.search([
            ('chorus_flux_number', '!=', False),
            '|', ('chorus_flux_status', '=', False),
            '&', ('chorus_flux_status', 'not ilike', 'INTEGRE'),
            ('chorus_flux_status', 'not ilike', 'REJET'),
        ])
        for move in moves:
            if not move.company_id.chorus_api_active:
                continue
            previous_status = move.chorus_flux_status
            try:
                move.action_check_chorus_status()
            except Exception:
                _logger.warning("Cron Chorus Pro : échec flux %s (%s)", move.chorus_flux_number, move.display_name, exc_info=True)
                continue
            status = move.chorus_flux_status or ''
            if 'REJET' in status.upper() and status != previous_status:
                user = move.invoice_user_id or self.env.ref('base.user_admin', raise_if_not_found=False)
                if user and user.active:
                    move.activity_schedule(
                        'mail.mail_activity_data_todo', user_id=user.id,
                        summary=_("Flux Chorus Pro rejeté"),
                        note=_("Le flux %(f)s de %(m)s a été rejeté (statut : %(s)s).", f=move.chorus_flux_number, m=move.display_name, s=status),
                    )
        return True

    @api.onchange('mandat_sale_order_id')
    def _onchange_bca_source(self):
        so = self.mandat_sale_order_id
        if so:
            self.is_mandat_administratif = True
            self.mandat_numero           = so.mandat_numero
            self.numero_engagement       = so.numero_engagement
            self.acheteur_siret          = so.acheteur_siret
            self.reference_bon_commande  = so.reference_bon_commande
            self.ordonnateur             = so.ordonnateur
            self.qualite_ordonnateur     = so.qualite_ordonnateur
            self.comptable_public        = so.comptable_public
            self.structure_chorus        = so.structure_chorus
            self.service_chorus          = so.service_chorus
            self.service_fait_certifie   = so.service_fait_certifie
            self.date_service_fait       = so.date_service_fait
            self.certificateur_sf        = so.certificateur_service_fait
