# -*- coding: utf-8 -*-
import base64
import re

from odoo import _, api, fields, models
from odoo.exceptions import UserError

CHORUS_PRO_URL = "https://portail.chorus-pro.gouv.fr"

FLUX_SYNTAXES = {
    'facturx': 'IN_DP_E2_FACTURX',
    'cii': 'IN_DP_E1_CII_16B',
    'ubl': 'IN_DP_E1_UBL_INVOICE',
}


class AccountMove(models.Model):
    _inherit = 'account.move'

    is_public_entity_partner = fields.Boolean(
        related='partner_id.commercial_partner_id.is_public_entity',
        string="Client entité publique",
    )
    engagement_juridique = fields.Char(
        string="N° d'engagement juridique",
        copy=False,
        help="Numéro d'engagement juridique (bon de commande) de l'entité "
             "publique, à renseigner lors du dépôt sur Chorus Pro.",
    )
    chorus_service_code = fields.Char(
        string="Code service (Chorus Pro)",
        compute='_compute_chorus_service_code',
        store=True,
        readonly=False,
        copy=False,
    )
    chorus_sent = fields.Boolean(
        string="Déposée sur Chorus Pro",
        copy=False,
        tracking=True,
    )
    chorus_sent_date = fields.Datetime(
        string="Date de dépôt Chorus Pro",
        copy=False,
    )
    chorus_flux_number = fields.Char(
        string="N° de flux Chorus Pro",
        copy=False,
        readonly=True,
        help="Numéro de flux (numeroFluxDepot) renvoyé par Chorus Pro lors "
             "du dépôt via l'API PISTE.",
    )
    chorus_flux_status = fields.Char(
        string="Statut du flux Chorus Pro",
        copy=False,
        readonly=True,
    )

    @api.depends('partner_id')
    def _compute_chorus_service_code(self):
        for move in self:
            if not move.chorus_service_code:
                move.chorus_service_code = (
                    move.partner_id.commercial_partner_id.chorus_service_code
                )

    def action_mark_chorus_sent(self):
        """Marquer la facture comme déposée sur Chorus Pro."""
        for move in self:
            move.write({
                'chorus_sent': True,
                'chorus_sent_date': fields.Datetime.now(),
            })
            move.message_post(
                body=_("Facture déposée sur Chorus Pro le %s.",
                       fields.Datetime.now().strftime('%d/%m/%Y %H:%M')),
            )
        return True

    def action_reset_chorus_sent(self):
        """Annuler le marquage de dépôt Chorus Pro."""
        self.write({'chorus_sent': False, 'chorus_sent_date': False})
        return True

    def action_open_chorus_pro(self):
        """Ouvrir le portail Chorus Pro dans un nouvel onglet."""
        return {
            'type': 'ir.actions.act_url',
            'url': CHORUS_PRO_URL,
            'target': 'new',
        }

    # === ENVOI AUTOMATIQUE VIA L'API PISTE / AIFE === #

    def _chorus_get_flux_file(self):
        """Construire le fichier à déposer selon la syntaxe configurée.

        :return: tuple (nom_fichier, contenu_bytes)
        """
        self.ensure_one()
        syntax = self.company_id.chorus_flux_syntax or 'facturx'
        base_name = re.sub(r'[^A-Za-z0-9_-]', '_', self.name or 'FACTURE')

        if syntax == 'facturx':
            attachment = self.invoice_pdf_report_id
            if not attachment or not attachment.raw:
                raise UserError(_(
                    "Aucun PDF Factur-X n'a encore été généré pour %s.\n"
                    "Utilisez d'abord « Imprimer et envoyer » (le PDF Odoo "
                    "intègre nativement le XML Factur-X), puis relancez "
                    "l'envoi vers Chorus Pro.", self.display_name,
                ))
            return f"{base_name}.pdf", attachment.raw

        builder_model = (
            'account.edi.xml.cii' if syntax == 'cii'
            else 'account.edi.xml.ubl_21'
        )
        builder = self.env[builder_model]
        result = builder._export_invoice(self)
        # _export_invoice renvoie (contenu, erreurs) selon les versions.
        content, errors = (
            result if isinstance(result, (tuple, list)) else (result, None)
        )
        if errors:
            raise UserError(_(
                "Erreurs lors de la génération du fichier %(syntax)s pour "
                "%(move)s :\n%(errors)s",
                syntax=syntax.upper(), move=self.display_name,
                errors="\n".join(str(e) for e in errors),
            ))
        if isinstance(content, str):
            content = content.encode('utf-8')
        return f"{base_name}.xml", content

    def action_send_to_chorus(self):
        """Déposer la facture sur Chorus Pro via l'API PISTE
        (service deposerFluxFacture)."""
        for move in self:
            company = move.company_id
            if not company.chorus_api_active:
                raise UserError(_(
                    "L'envoi automatique Chorus Pro n'est pas activé.\n"
                    "Comptabilité → Configuration → Paramètres → Chorus Pro."
                ))
            if move.move_type not in ('out_invoice', 'out_refund'):
                raise UserError(_(
                    "Seules les factures et avoirs clients peuvent être "
                    "déposés sur Chorus Pro."))
            if move.state != 'posted':
                raise UserError(_(
                    "La facture %s doit être comptabilisée avant l'envoi "
                    "sur Chorus Pro.", move.display_name))
            partner = move.partner_id.commercial_partner_id
            if not partner.is_public_entity:
                raise UserError(_(
                    "Le client %s n'est pas marqué « Entité publique » : "
                    "le dépôt Chorus Pro ne le concerne pas.", partner.name))
            if not partner.chorus_siret:
                raise UserError(_(
                    "Renseignez le SIRET destinataire Chorus Pro sur la "
                    "fiche de %s avant l'envoi.", partner.name))
            if (partner.chorus_engagement_required
                    and not move.engagement_juridique):
                raise UserError(_(
                    "Cette structure exige un n° d'engagement juridique : "
                    "renseignez-le sur la facture %s avant l'envoi.",
                    move.display_name))

            filename, content = move._chorus_get_flux_file()
            syntax_code = FLUX_SYNTAXES[
                company.chorus_flux_syntax or 'facturx']
            result = company._chorus_request(
                '/cpro/factures/v1/deposer/flux',
                {
                    'fichierFlux': base64.b64encode(content).decode(),
                    'nomFichier': filename,
                    'syntaxeFlux': syntax_code,
                    'avecSignature': False,
                },
            )
            flux_number = result.get('numeroFluxDepot')
            move.write({
                'chorus_sent': True,
                'chorus_sent_date': fields.Datetime.now(),
                'chorus_flux_number': flux_number,
                'chorus_flux_status': _("Déposé — en cours de traitement"),
            })
            move.message_post(body=_(
                "Facture déposée sur Chorus Pro via l'API PISTE "
                "(%(mode)s).<br/>Fichier : %(file)s — Syntaxe : %(syntax)s"
                "<br/>N° de flux : <b>%(flux)s</b>",
                mode=company.chorus_api_mode,
                file=filename, syntax=syntax_code,
                flux=flux_number or _("non communiqué"),
            ))
        return True

    def action_check_chorus_status(self):
        """Consulter le compte rendu de traitement du flux déposé
        (service ConsulterCR)."""
        for move in self:
            if not move.chorus_flux_number:
                raise UserError(_(
                    "Aucun numéro de flux Chorus Pro sur %s : la facture "
                    "n'a pas été déposée via l'API.", move.display_name))
            result = move.company_id._chorus_request(
                '/cpro/transverses/v1/consulterCR',
                {'numeroFluxDepot': move.chorus_flux_number},
            )
            status = (
                result.get('etatCourantFlux')
                or result.get('statutFlux')
                or result.get('libelle')
                or _("statut inconnu")
            )
            move.chorus_flux_status = status
            move.message_post(body=_(
                "Statut du flux Chorus Pro %(flux)s : <b>%(status)s</b>",
                flux=move.chorus_flux_number, status=status,
            ))
        return True
