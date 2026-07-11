# -*- coding: utf-8 -*-
from odoo import _, api, fields, models
from odoo.exceptions import ValidationError

PUBLIC_ENTITY_TYPES = [
    ('state_local', "État, collectivité territoriale ou EPA — 30 jours"),
    ('health', "Établissement public de santé — 50 jours"),
    ('public_company', "Entreprise publique — 60 jours"),
]

PUBLIC_ENTITY_DELAYS = {
    'state_local': 30,
    'health': 50,
    'public_company': 60,
}

PUBLIC_ENTITY_TERMS = {
    'state_local': 'mandat_administratif.payment_term_mandat_30',
    'health': 'mandat_administratif.payment_term_mandat_50',
    'public_company': 'mandat_administratif.payment_term_mandat_60',
}


class ResPartner(models.Model):
    _inherit = 'res.partner'

    is_public_entity = fields.Boolean(
        string="Entité publique (mandat administratif)",
        help="Administration, collectivité territoriale ou établissement "
             "public réglant par mandat administratif. Active le mode de "
             "paiement « Mandat administratif » au checkout et le bloc "
             "Chorus Pro sur les factures.",
    )
    public_entity_type = fields.Selection(
        selection=PUBLIC_ENTITY_TYPES,
        string="Type de structure publique",
        help="Détermine le délai global de paiement légal (30, 50 ou "
             "60 jours) et le terme de paiement appliqué automatiquement. "
             "Le client peut le déclarer lui-même depuis son portail "
             "(/my/mandat-administratif).",
    )
    public_payment_delay = fields.Integer(
        string="Délai global de paiement (jours)",
        compute='_compute_public_payment_delay',
        store=True,
        help="Délai légal de règlement par le comptable public, déduit du "
             "type de structure.",
    )

    @api.depends('public_entity_type', 'is_public_entity')
    def _compute_public_payment_delay(self):
        for partner in self:
            if partner.is_public_entity:
                partner.public_payment_delay = PUBLIC_ENTITY_DELAYS.get(
                    partner.public_entity_type, 30)
            else:
                partner.public_payment_delay = 0

    def _apply_public_payment_term(self):
        """Affecter le terme de paiement correspondant au type de structure
        (utilisé par l'onchange backend et le formulaire portail)."""
        for partner in self:
            xmlid = PUBLIC_ENTITY_TERMS.get(partner.public_entity_type)
            if not (partner.is_public_entity and xmlid):
                continue
            term = self.env.ref(xmlid, raise_if_not_found=False)
            if term:
                partner.property_payment_term_id = term

    @api.onchange('public_entity_type', 'is_public_entity')
    def _onchange_public_entity_type(self):
        if self.is_public_entity and self.public_entity_type:
            xmlid = PUBLIC_ENTITY_TERMS.get(self.public_entity_type)
            term = self.env.ref(xmlid, raise_if_not_found=False)
            if term:
                self.property_payment_term_id = term

    def _notify_public_entity_declaration(self):
        """Tracer l'auto-déclaration portail et créer une activité de
        vérification pour l'équipe (contrôle humain avant la première
        commande en mandat administratif)."""
        self.ensure_one()
        type_label = dict(PUBLIC_ENTITY_TYPES).get(
            self.public_entity_type, _("non renseigné"))
        body = _(
            "<b>Auto-déclaration d'entité publique via le portail.</b><br/>"
            "Type de structure : %(type)s<br/>"
            "Délai global de paiement appliqué : %(delay)s jours<br/>"
            "SIRET : %(siret)s — Code service : %(service)s<br/>"
            "Engagement juridique exigé : %(engagement)s",
            type=type_label,
            delay=self.public_payment_delay,
            siret=self.chorus_siret or _("non renseigné"),
            service=self.chorus_service_code or _("non renseigné"),
            engagement=_("oui") if self.chorus_engagement_required
            else _("non"),
        )
        self.message_post(body=body)
        user = self.user_id or self.env.ref(
            'base.user_admin', raise_if_not_found=False)
        if user and user.active:
            self.activity_schedule(
                'mail.mail_activity_data_todo',
                user_id=user.id,
                summary=_("Vérifier l'auto-déclaration d'entité publique"),
                note=body,
            )
    chorus_siret = fields.Char(
        string="SIRET destinataire (Chorus Pro)",
        size=14,
        help="SIRET de la structure publique destinataire de la facture "
             "sur Chorus Pro (14 chiffres).",
    )
    chorus_service_code = fields.Char(
        string="Code service (Chorus Pro)",
        help="Code service exécutant tel que paramétré sur Chorus Pro "
             "(obligatoire pour certaines structures, ex. FACTURES_PUBLIQUES).",
    )
    chorus_engagement_required = fields.Boolean(
        string="Engagement juridique obligatoire",
        help="La structure exige un numéro d'engagement juridique (bon de "
             "commande) pour accepter la facture sur Chorus Pro.",
    )

    @api.constrains('chorus_siret')
    def _check_chorus_siret(self):
        for partner in self.filtered('chorus_siret'):
            siret = partner.chorus_siret.replace(' ', '')
            if not (siret.isdigit() and len(siret) == 14):
                raise ValidationError(
                    _("Le SIRET Chorus Pro doit comporter exactement "
                      "14 chiffres.")
                )
            # Exception La Poste : les SIRET commençant par 356000000
            # ne respectent pas la clé de Luhn.
            if not siret.startswith('356000000') and not self._luhn_valid(siret):
                raise ValidationError(
                    _("Le SIRET Chorus Pro « %s » est invalide "
                      "(clé de contrôle incorrecte).", siret)
                )

    @staticmethod
    def _luhn_valid(number):
        total = 0
        for i, digit in enumerate(reversed(number)):
            d = int(digit)
            if i % 2 == 1:
                d *= 2
                if d > 9:
                    d -= 9
            total += d
        return total % 10 == 0
