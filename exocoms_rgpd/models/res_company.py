# -*- coding: utf-8 -*-
from odoo import fields, models


class ResCompany(models.Model):
    _inherit = "res.company"

    rgpd_dpo_user_id = fields.Many2one(
        "res.users", string="Délégué à la protection des données"
    )
    rgpd_dpo_name = fields.Char(string="Nom du DPO affiché")
    rgpd_dpo_email = fields.Char(string="E-mail de contact RGPD")
    rgpd_dpo_phone = fields.Char(string="Téléphone du DPO")
    rgpd_dpo_address = fields.Text(string="Adresse postale pour les demandes")
    rgpd_authority_name = fields.Char(
        string="Autorité de contrôle", default="CNIL"
    )
    rgpd_authority_url = fields.Char(
        string="URL de réclamation", default="https://www.cnil.fr/fr/plaintes"
    )
    rgpd_portal_enabled = fields.Boolean(
        string="Espace RGPD sur le portail", default=True
    )
    rgpd_public_form_enabled = fields.Boolean(
        string="Formulaire public de demande", default=True
    )
    rgpd_auto_acknowledge = fields.Boolean(
        string="Accusé de réception automatique", default=True
    )
    rgpd_privacy_policy_url = fields.Char(
        string="URL de la politique de confidentialité", default="/politique-de-confidentialite"
    )
    rgpd_blacklist_sync = fields.Boolean(
        string="Synchroniser avec la liste noire de messagerie", default=True,
        help="Un retrait de consentement marketing met l'adresse en liste noire "
        "d'Odoo, et une désinscription depuis une campagne est journalisée "
        "comme un retrait. Sans cette option, un retrait enregistré "
        "n'empêcherait pas l'envoi de la campagne suivante.",
    )

    # ------------------------------------------------------------------
    # Séquences par société
    # ------------------------------------------------------------------
    # Le module livre trois séquences partagées (company_id vide) : les
    # références sont alors continues sur l'ensemble du groupe. Une société qui
    # doit numéroter séparément se voit créer ses propres séquences, que
    # ``with_company()`` retient automatiquement à la place des partagées.
    RGPD_SEQUENCES = [
        ("exocoms.rgpd.request", "RGPD - Demande de droits", "RGPD/%(year)s/", 4),
        ("exocoms.rgpd.treatment", "RGPD - Traitement", "TRT/%(year)s/", 4),
        ("exocoms.rgpd.breach", "RGPD - Violation de données", "VIOL/%(year)s/", 3),
    ]

    def _rgpd_create_sequences(self):
        """Crée les séquences RGPD propres à chaque société de ``self``.

        Idempotent : une société déjà dotée d'une séquence pour un code donné
        est ignorée, afin que l'appel puisse être rejoué sans créer de doublon
        ni réinitialiser un compteur en cours.
        """
        Sequence = self.env["ir.sequence"].sudo()
        created = Sequence
        for company in self:
            for code, name, prefix, padding in self.RGPD_SEQUENCES:
                existing = Sequence.search(
                    [("code", "=", code), ("company_id", "=", company.id)], limit=1
                )
                if existing:
                    continue
                created |= Sequence.create(
                    {
                        "name": "%s (%s)" % (name, company.name),
                        "code": code,
                        "prefix": prefix,
                        "padding": padding,
                        "company_id": company.id,
                        "implementation": "standard",
                    }
                )
        return created

    def _rgpd_has_own_sequences(self):
        self.ensure_one()
        codes = [code for code, _n, _p, _pad in self.RGPD_SEQUENCES]
        return bool(
            self.env["ir.sequence"].sudo().search_count(
                [("code", "in", codes), ("company_id", "=", self.id)]
            )
        )
