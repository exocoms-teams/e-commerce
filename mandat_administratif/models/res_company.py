# -*- coding: utf-8 -*-
import base64
import logging

import requests

from odoo import _, fields, models
from odoo.exceptions import UserError

_logger = logging.getLogger(__name__)

CHORUS_TIMEOUT = 30

CHORUS_URLS = {
    'sandbox': {
        'oauth': 'https://sandbox-oauth.piste.gouv.fr/api/oauth/token',
        'api': 'https://sandbox-api.piste.gouv.fr',
    },
    'production': {
        'oauth': 'https://oauth.piste.gouv.fr/api/oauth/token',
        'api': 'https://api.piste.gouv.fr',
    },
}


class ResCompany(models.Model):
    _inherit = 'res.company'

    chorus_api_active = fields.Boolean(
        string="Envoi automatique Chorus Pro (API PISTE)",
        help="Active le dépôt des factures sur Chorus Pro via l'API PISTE "
             "de l'AIFE.",
    )
    chorus_api_mode = fields.Selection(
        selection=[
            ('sandbox', "Sandbox (qualification)"),
            ('production', "Production"),
        ],
        string="Environnement PISTE",
        default='sandbox',
        help="Commencez toujours par l'environnement Sandbox (portail de "
             "qualification Chorus Pro) avant de passer en production.",
    )
    chorus_piste_client_id = fields.Char(string="PISTE Client ID")
    chorus_piste_client_secret = fields.Char(string="PISTE Client Secret")
    chorus_technical_login = fields.Char(
        string="Compte technique Chorus Pro (login)",
        help="Identifiant du compte technique créé sur Chorus Pro "
             "(forme TECH_1_xxxx@cpro.fr).",
    )
    chorus_technical_password = fields.Char(
        string="Compte technique Chorus Pro (mot de passe)",
    )
    chorus_flux_syntax = fields.Selection(
        selection=[
            ('facturx', "Factur-X — PDF/A-3 (IN_DP_E2_FACTURX)"),
            ('cii', "XML CII 16B (IN_DP_E1_CII_16B)"),
            ('ubl', "XML UBL Invoice 2.1 (IN_DP_E1_UBL_INVOICE)"),
        ],
        string="Syntaxe de flux",
        default='facturx',
        help="Factur-X est recommandé : c'est le format des PDF de facture "
             "générés nativement par Odoo (XML CII intégré au PDF).",
    )

    # === CLIENT API PISTE / CHORUS PRO === #

    def _chorus_check_config(self):
        self.ensure_one()
        missing = []
        if not self.chorus_piste_client_id:
            missing.append("PISTE Client ID")
        if not self.chorus_piste_client_secret:
            missing.append("PISTE Client Secret")
        if not self.chorus_technical_login:
            missing.append("login du compte technique")
        if not self.chorus_technical_password:
            missing.append("mot de passe du compte technique")
        if missing:
            raise UserError(_(
                "Configuration Chorus Pro incomplète : %s.\n"
                "Renseignez ces informations dans "
                "Comptabilité → Configuration → Paramètres → Chorus Pro.",
                ", ".join(missing),
            ))

    def _chorus_get_urls(self):
        self.ensure_one()
        return CHORUS_URLS[self.chorus_api_mode or 'sandbox']

    def _chorus_get_token(self):
        """Obtenir un jeton OAuth2 PISTE (client_credentials, validité 1 h)."""
        self.ensure_one()
        self._chorus_check_config()
        urls = self._chorus_get_urls()
        try:
            response = requests.post(
                urls['oauth'],
                headers={'Content-Type': 'application/x-www-form-urlencoded'},
                data={
                    'grant_type': 'client_credentials',
                    'client_id': self.chorus_piste_client_id,
                    'client_secret': self.chorus_piste_client_secret,
                    'scope': 'openid',
                },
                timeout=CHORUS_TIMEOUT,
            )
        except requests.exceptions.RequestException as error:
            raise UserError(_(
                "Connexion à PISTE impossible : %s", error,
            )) from error
        if response.status_code == 401:
            raise UserError(_(
                "Authentification PISTE échouée (401) : Vérifiez le Client ID et le Client Secret."
            ))
        elif response.status_code == 403:
            raise UserError(_(
                "Accès refusé par Chorus Pro (403) : Vérifiez vos CGU et les droits associés à votre compte technique."
            ))
        if response.status_code != 200:
            raise UserError(_(
                "Échec de l'authentification PISTE (HTTP %(code)s) : "
                "%(body)s\nVérifiez le Client ID / Client Secret et "
                "l'activation de l'API « Factures » sur votre application "
                "PISTE.",
                code=response.status_code, body=response.text[:500],
            ))
        token = response.json().get('access_token')
        if not token:
            raise UserError(_("PISTE n'a pas renvoyé de jeton d'accès."))
        return token

    def _chorus_request(self, path, payload):
        """Appeler un service Chorus Pro (toutes les opérations sont en POST).

        :param path: chemin du service, ex. '/cpro/factures/v1/deposer/flux'
        :param payload: dict sérialisé en JSON
        :return: dict de la réponse JSON
        """
        self.ensure_one()
        token = self._chorus_get_token()
        urls = self._chorus_get_urls()
        cpro_account = base64.b64encode(
            f"{self.chorus_technical_login}:"
            f"{self.chorus_technical_password}".encode()
        ).decode()
        try:
            response = requests.post(
                urls['api'] + path,
                headers={
                    'Authorization': f'Bearer {token}',
                    'cpro-account': cpro_account,
                    'Content-Type': 'application/json;charset=utf-8',
                },
                json=payload,
                timeout=CHORUS_TIMEOUT,
            )
        except requests.exceptions.RequestException as error:
            raise UserError(_(
                "Appel Chorus Pro impossible (%(path)s) : %(error)s",
                path=path, error=error,
            )) from error
        if response.status_code != 200:
            raise UserError(_(
                "Erreur Chorus Pro sur %(path)s (HTTP %(code)s) : %(body)s",
                path=path, code=response.status_code,
                body=response.text[:500],
            ))
        result = response.json()
        # codeRetour 0 = succès ; toujours le vérifier même en HTTP 200.
        if result.get('codeRetour') not in (0, '0', None):
            raise UserError(_(
                "Chorus Pro a refusé la demande (%(path)s) : "
                "code %(code)s — %(libelle)s",
                path=path, code=result.get('codeRetour'),
                libelle=result.get('libelle') or _("sans libellé"),
            ))
        return result

    def action_test_chorus_connection(self):
        """Tester l'authentification PISTE + compte technique."""
        self.ensure_one()
        # 1. Jeton OAuth
        self._chorus_get_token()
        # 2. Appel léger authentifié par le compte technique
        self._chorus_request(
            '/cpro/utilisateurs/v1/monCompte/recuperer/rattachements',
            {'parametresRecherche': {
                'nbResultatsParPage': 1,
                'pageResultatDemandee': 1,
            }},
        )
        return {
            'type': 'ir.actions.client',
            'tag': 'display_notification',
            'params': {
                'type': 'success',
                'title': _("Chorus Pro"),
                'message': _(
                    "Connexion réussie (environnement %s).",
                    dict(self._fields['chorus_api_mode'].selection).get(
                        self.chorus_api_mode
                    ),
                ),
                'sticky': False,
            },
        }
