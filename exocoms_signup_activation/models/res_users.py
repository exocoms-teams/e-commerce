# -*- coding: utf-8 -*-
import logging
import secrets
from datetime import timedelta

from odoo import _, api, fields, models
from odoo.exceptions import UserError

_logger = logging.getLogger(__name__)

PARAM_PREFIX = 'exocoms_signup_activation.'

DEFAULTS = {
    'token_ttl_hours': 24,
    'purge_days': 7,
    'resend_interval': 120,
    'max_resend': 5,
}


class ResUsers(models.Model):
    _inherit = 'res.users'

    exocoms_email_verified = fields.Boolean(
        string="Adresse email vérifiée",
        default=True, copy=False,
        help="Décoché tant que l'utilisateur n'a pas cliqué sur le lien "
             "d'activation reçu par email lors de son inscription.")
    exocoms_activation_token = fields.Char(
        string="Jeton d'activation", copy=False, groups='base.group_system')
    exocoms_activation_url = fields.Char(
        string="Lien d'activation", copy=False, groups='base.group_system',
        help="Lien complet envoyé au client. Il est construit à partir du "
             "domaine du site web sur lequel l'inscription a été déposée, ce "
             "qui garantit un lien cohérent en multi-société / multi-site.")
    exocoms_activation_expiry = fields.Datetime(
        string="Expiration du jeton", copy=False, groups='base.group_system')
    exocoms_activation_sent_date = fields.Datetime(
        string="Dernier envoi d'activation", copy=False, groups='base.group_system')
    exocoms_activation_email_count = fields.Integer(
        string="Nombre d'emails d'activation envoyés",
        default=0, copy=False, groups='base.group_system')
    exocoms_activation_date = fields.Datetime(
        string="Date d'activation", readonly=True, copy=False)

    # ------------------------------------------------------------------
    # Paramètres
    # ------------------------------------------------------------------
    @api.model
    def _exocoms_get_int_param(self, key):
        raw = self.env['ir.config_parameter'].sudo().get_param(
            PARAM_PREFIX + key, DEFAULTS[key])
        try:
            return int(raw)
        except (TypeError, ValueError):
            return DEFAULTS[key]

    # ------------------------------------------------------------------
    # Cycle de vie de l'activation
    # ------------------------------------------------------------------
    def _exocoms_prepare_activation(self, base_url=None):
        """Génère un nouveau jeton à usage unique et archive le compte.

        Le compte reste archivé (``active = False``) tant que l'adresse email
        n'est pas confirmée : aucune connexion n'est possible entre-temps.

        :param base_url: racine d'URL à utiliser pour le lien d'activation.
            En multi-société / multi-site, le contrôleur transmet le domaine du
            site sur lequel l'inscription a été déposée. À défaut, on retombe
            sur le site de la société de l'utilisateur, puis sur ``web.base.url``.
        """
        self.ensure_one()
        user = self.sudo()
        if not user.share:
            raise UserError(_(
                "L'activation par email ne concerne que les comptes portail. "
                "Le compte « %s » est un utilisateur interne.", user.login))
        if user.exocoms_email_verified and user.active:
            raise UserError(_(
                "Le compte « %s » est déjà activé. Relancer une activation le "
                "désactiverait ; utilisez plutôt la réinitialisation de mot de "
                "passe.", user.login))
        ttl = self._exocoms_get_int_param('token_ttl_hours')
        token = secrets.token_urlsafe(32)
        root = (base_url or user._exocoms_default_base_url()).rstrip('/')
        user.write({
            'exocoms_activation_token': token,
            'exocoms_activation_url': '%s/signup/activate/%s' % (root, token),
            'exocoms_activation_expiry': fields.Datetime.now() + timedelta(hours=ttl),
            'exocoms_email_verified': False,
            'exocoms_activation_date': False,
            'active': False,
        })
        return user.exocoms_activation_token

    def _exocoms_default_base_url(self):
        """Domaine à utiliser lorsque le contrôleur n'en fournit pas.

        Ordre de résolution : site web rattaché à la société de l'utilisateur,
        puis paramètre système ``web.base.url``. Cela couvre les envois déclenchés
        hors requête HTTP (bouton back-office, script, cron).
        """
        self.ensure_one()
        website = self.env['website'].sudo().search(
            [('company_id', '=', self.company_id.id)], limit=1)
        if website and website.domain:
            domain = website.domain.strip()
            if not domain.startswith(('http://', 'https://')):
                domain = 'https://%s' % domain
            return domain
        return self.env['ir.config_parameter'].sudo().get_param('web.base.url') or ''

    def _exocoms_check_resend_allowed(self):
        """Contrôle de fréquence et de volume des emails d'activation.

        À appeler **avant** ``_exocoms_prepare_activation()`` : si le renvoi est
        refusé, le jeton en circulation ne doit pas être invalidé pour rien.
        Lève une ``UserError`` explicite en cas de refus.
        """
        self.ensure_one()
        user = self.sudo()
        interval = self._exocoms_get_int_param('resend_interval')
        max_resend = self._exocoms_get_int_param('max_resend')

        if interval and user.exocoms_activation_sent_date:
            elapsed = (fields.Datetime.now()
                       - user.exocoms_activation_sent_date).total_seconds()
            if elapsed < interval:
                raise UserError(_(
                    "Un email vient déjà d'être envoyé. Merci de patienter "
                    "%s secondes avant de demander un nouvel envoi.",
                    int(interval - elapsed)))

        if max_resend and user.exocoms_activation_email_count >= max_resend:
            raise UserError(_(
                "Le nombre maximum d'emails d'activation a été atteint pour "
                "ce compte. Merci de contacter notre support."))
        return True

    def _exocoms_send_activation_email(self, silent=False):
        """Envoie l'email contenant le lien d'activation.

        :param silent: si True, les limitations de fréquence/volume ne lèvent
            pas d'erreur (utilisé pour le tout premier envoi, juste après la
            création du compte).
        """
        self.ensure_one()
        user = self.sudo()
        now = fields.Datetime.now()

        if not silent:
            self._exocoms_check_resend_allowed()

        template = self.env.ref(
            'exocoms_signup_activation.mail_template_signup_activation',
            raise_if_not_found=False)
        if not template:
            _logger.error("Modèle d'email d'activation introuvable.")
            if not silent:
                raise UserError(_("Le modèle d'email d'activation est introuvable."))
            return False

        template.sudo().send_mail(user.id, force_send=True, raise_exception=False)
        user.write({
            'exocoms_activation_sent_date': now,
            'exocoms_activation_email_count': user.exocoms_activation_email_count + 1,
        })
        return True

    @api.model
    def _exocoms_activate_from_token(self, token):
        """Valide un jeton et réactive le compte correspondant.

        :return: tuple ``(user, state)`` où state vaut 'ok', 'expired',
            'already' ou 'invalid'.
        """
        if not token:
            return self.browse(), 'invalid'

        Users = self.sudo().with_context(active_test=False)
        user = Users.search([('exocoms_activation_token', '=', token)], limit=1)
        if not user:
            # Jeton déjà consommé : on ne sait pas à qui il appartenait.
            return self.browse(), 'invalid'

        if user.exocoms_email_verified:
            return user, 'already'

        expiry = user.exocoms_activation_expiry
        if expiry and expiry < fields.Datetime.now():
            return user, 'expired'

        user.write({
            'active': True,
            'exocoms_email_verified': True,
            'exocoms_activation_token': False,
            'exocoms_activation_url': False,
            'exocoms_activation_expiry': False,
            'exocoms_activation_date': fields.Datetime.now(),
        })
        if user.partner_id and not user.partner_id.active:
            user.partner_id.sudo().write({'active': True})

        _logger.info("Compte portail activé : %s", user.login)
        return user, 'ok'

    @api.model
    def _exocoms_find_pending(self, login):
        """Retourne le compte non activé correspondant à cet identifiant."""
        if not login:
            return self.browse()
        return self.sudo().with_context(active_test=False).search([
            ('login', '=', login.strip()),
            ('exocoms_email_verified', '=', False),
            ('active', '=', False),
        ], limit=1)

    # ------------------------------------------------------------------
    # Back-office
    # ------------------------------------------------------------------
    def action_exocoms_resend_activation(self):
        """Bouton « Renvoyer l'email d'activation » sur la fiche utilisateur."""
        for user in self:
            user._exocoms_prepare_activation()
            user._exocoms_send_activation_email(silent=True)
        return {
            'type': 'ir.actions.client',
            'tag': 'display_notification',
            'params': {
                'type': 'success',
                'title': _("Email envoyé"),
                'message': _("Le lien d'activation a été renvoyé."),
                'sticky': False,
            },
        }

    def action_exocoms_force_activation(self):
        """Active manuellement un compte sans passer par l'email."""
        for user in self:
            user.sudo().write({
                'active': True,
                'exocoms_email_verified': True,
                'exocoms_activation_token': False,
                'exocoms_activation_url': False,
                'exocoms_activation_expiry': False,
                'exocoms_activation_date': fields.Datetime.now(),
            })
        return True

    # ------------------------------------------------------------------
    # Purge automatique
    # ------------------------------------------------------------------
    @api.model
    def _cron_exocoms_purge_pending(self):
        """Supprime les inscriptions jamais activées (hygiène RGPD)."""
        days = self._exocoms_get_int_param('purge_days')
        if days <= 0:
            return True

        limit_date = fields.Datetime.now() - timedelta(days=days)
        # Le domaine est volontairement restrictif : on ne supprime que des
        # comptes portail, archivés, jamais vérifiés ET porteurs d'un jeton
        # d'activation. Un utilisateur interne archivé manuellement par un
        # administrateur ne peut donc jamais être happé par la purge.
        users = self.sudo().with_context(active_test=False).search([
            ('exocoms_email_verified', '=', False),
            ('exocoms_activation_token', '!=', False),
            ('active', '=', False),
            ('share', '=', True),
            ('create_date', '<', limit_date),
        ])
        removed = 0
        for user in users:
            partner = user.partner_id
            login = user.login
            try:
                with self.env.cr.savepoint():
                    user.unlink()
                removed += 1
            except Exception as exc:  # noqa: BLE001 - dépendances métier possibles
                _logger.warning(
                    "Purge impossible pour l'inscription %s : %s", login, exc)
                continue
            try:
                with self.env.cr.savepoint():
                    if partner.exists() and not partner.user_ids:
                        partner.unlink()
            except Exception:  # noqa: BLE001 - partenaire référencé ailleurs
                _logger.info(
                    "Partenaire conservé (référencé ailleurs) pour %s", login)

        if removed:
            _logger.info("Purge des inscriptions non activées : %s compte(s) supprimé(s)", removed)
        return True
