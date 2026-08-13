# -*- coding: utf-8 -*-
import logging
import re
import secrets
from datetime import timedelta

from odoo import _, api, fields, models
from odoo.exceptions import UserError

_logger = logging.getLogger(__name__)

PARAM_PREFIX = 'exocoms_portal_signup.'

DEFAULTS = {
    'token_ttl_hours': 24,
    'purge_days': 7,
    'resend_interval': 120,
    'max_resend': 5,
}

# Volontairement permissif : le but est d'écarter les saisies manifestement
# erronées, pas de réimplémenter la RFC 5322.
EMAIL_RE = re.compile(r"^[^@\s]+@[^@\s]+\.[A-Za-z]{2,}$")


class ResUsers(models.Model):
    _inherit = 'res.users'

    exocoms_email_verified = fields.Boolean(
        string="Email vérifié", default=True, copy=False, readonly=True,
        help="Décoché tant que le client n'a pas cliqué sur le lien "
             "d'activation reçu par email. Les comptes créés autrement que "
             "par le formulaire public sont considérés comme vérifiés.")
    exocoms_activation_token = fields.Char(
        string="Jeton d'activation", copy=False, groups='base.group_system')
    exocoms_activation_url = fields.Char(
        string="Lien d'activation", copy=False, groups='base.group_system',
        help="Lien complet envoyé au client, construit à partir du domaine du "
             "site sur lequel l'inscription a été déposée.")
    exocoms_activation_expiry = fields.Datetime(
        string="Expiration du lien", copy=False, groups='base.group_system')
    exocoms_activation_sent_date = fields.Datetime(
        string="Dernier envoi", copy=False, readonly=True)
    exocoms_activation_email_count = fields.Integer(
        string="Emails envoyés", default=0, copy=False, readonly=True)
    exocoms_activation_date = fields.Datetime(
        string="Date d'activation", copy=False, readonly=True)

    # ------------------------------------------------------------------
    # Paramétrage
    # ------------------------------------------------------------------
    @api.model
    def _exocoms_get_int_param(self, key):
        raw = self.env['ir.config_parameter'].sudo().get_param(
            PARAM_PREFIX + key, DEFAULTS.get(key, 0))
        try:
            return int(raw)
        except (TypeError, ValueError):
            return DEFAULTS.get(key, 0)

    @api.model
    def _exocoms_get_bool_param(self, key, default=True):
        raw = self.env['ir.config_parameter'].sudo().get_param(PARAM_PREFIX + key)
        if raw is None or raw is False:
            return default
        return str(raw).strip().lower() not in ('', '0', 'false')

    # ------------------------------------------------------------------
    # Vérification de l'adresse email
    # ------------------------------------------------------------------
    @api.model
    def _exocoms_check_email(self, email):
        """Valide une adresse avant création du compte.

        Lève une ``UserError`` dont le message est affiché tel quel sur le
        formulaire d'inscription. Retourne l'adresse normalisée.
        """
        address = (email or '').strip().lower()
        if not EMAIL_RE.match(address):
            raise UserError(_("Cette adresse email n'est pas valide."))

        domain = address.rsplit('@', 1)[-1]
        Domains = self.env['exocoms.signup.domain']

        if self._exocoms_get_bool_param('block_disposable', True):
            if domain in Domains._exocoms_domain_list('blocked'):
                raise UserError(_(
                    "Les adresses email jetables ne sont pas acceptées. "
                    "Merci d'utiliser une adresse professionnelle ou "
                    "personnelle permanente."))

        if self._exocoms_get_bool_param('restrict_allowed', False):
            allowed = Domains._exocoms_domain_list('allowed')
            if allowed and domain not in allowed:
                raise UserError(_(
                    "Les inscriptions ne sont ouvertes qu'à une liste de "
                    "domaines autorisés. Merci de contacter notre support."))

        if self._exocoms_get_bool_param('check_mx', True):
            self._exocoms_check_mx(domain)

        return address

    @api.model
    def _exocoms_check_mx(self, domain):
        """Vérifie que le domaine peut recevoir du courrier.

        Dégradation propre : si ``dnspython`` est absent de l'environnement ou
        si la résolution échoue pour une raison technique (timeout, réseau),
        l'inscription n'est pas bloquée. On ne refuse que sur une réponse DNS
        explicitement négative.
        """
        try:
            import dns.resolver  # noqa: PLC0415
        except ImportError:
            _logger.info(
                "dnspython absent : contrôle MX ignoré pour le domaine %s", domain)
            return True

        resolver = dns.resolver.Resolver()
        resolver.lifetime = 5
        resolver.timeout = 5
        try:
            answers = resolver.resolve(domain, 'MX')
            if answers:
                return True
        except (dns.resolver.NXDOMAIN, dns.resolver.NoAnswer):
            # Certains domaines n'ont pas de MX mais un A : c'est un repli
            # légitime pour la remise de courrier.
            try:
                if resolver.resolve(domain, 'A'):
                    return True
            except Exception:  # noqa: BLE001
                pass
            raise UserError(_(
                "Le domaine « %s » ne semble pas pouvoir recevoir d'emails. "
                "Merci de vérifier votre adresse.", domain))
        except Exception as exc:  # noqa: BLE001
            _logger.info("Contrôle MX indisponible pour %s : %s", domain, exc)
            return True
        return True

    # ------------------------------------------------------------------
    # Recherche
    # ------------------------------------------------------------------
    @api.model
    def _exocoms_find_pending(self, login):
        """Inscription déposée mais jamais activée, pour un login donné."""
        if not login:
            return self.browse()
        Users = self.sudo().with_context(active_test=False)
        return Users.search(
            [('login', '=ilike', login.strip()),
             ('exocoms_email_verified', '=', False),
             ('exocoms_activation_token', '!=', False)],
            limit=1)

    # ------------------------------------------------------------------
    # Cycle de vie de l'activation
    # ------------------------------------------------------------------
    def _exocoms_default_base_url(self):
        """Domaine à utiliser hors requête HTTP (bouton back-office, cron)."""
        self.ensure_one()
        website = self.env['website'].sudo().search(
            [('company_id', '=', self.company_id.id)], limit=1)
        if website and website.domain:
            domain = website.domain.strip()
            if not domain.startswith(('http://', 'https://')):
                domain = 'https://%s' % domain
            return domain
        return self.env['ir.config_parameter'].sudo().get_param('web.base.url') or ''

    def _exocoms_prepare_activation(self, base_url=None):
        """Génère un jeton à usage unique et archive le compte."""
        self.ensure_one()
        user = self.sudo()
        if not user.share:
            raise UserError(_(
                "L'activation par email ne concerne que les comptes portail. "
                "« %s » est un utilisateur interne.", user.login))
        if user.exocoms_email_verified and user.active:
            raise UserError(_(
                "Le compte « %s » est déjà activé. Relancer une activation le "
                "désactiverait ; utilisez la réinitialisation de mot de passe.",
                user.login))

        token = secrets.token_urlsafe(32)
        root = (base_url or user._exocoms_default_base_url()).rstrip('/')
        user.write({
            'active': False,
            'exocoms_email_verified': False,
            'exocoms_activation_token': token,
            'exocoms_activation_url': '%s/signup/activate/%s' % (root, token),
            'exocoms_activation_expiry': fields.Datetime.now() + timedelta(
                hours=self._exocoms_get_int_param('token_ttl_hours')),
        })
        return token

    def _exocoms_check_resend_allowed(self):
        """Contrôle de fréquence et de volume.

        À appeler **avant** ``_exocoms_prepare_activation()`` : un renvoi refusé
        ne doit pas invalider le lien déjà reçu par le client.
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
                    "Un email vient d'être envoyé. Merci de patienter %s "
                    "secondes avant d'en demander un nouveau.",
                    int(interval - elapsed)))

        if max_resend and user.exocoms_activation_email_count >= max_resend:
            raise UserError(_(
                "Le nombre maximum d'emails d'activation a été atteint pour ce "
                "compte. Merci de contacter notre support."))
        return True

    def _exocoms_send_activation_email(self):
        """Envoie l'email d'activation. Ne contrôle pas les quotas."""
        self.ensure_one()
        user = self.sudo()
        template = self.env.ref(
            'exocoms_portal_signup.mail_template_signup_activation',
            raise_if_not_found=False)
        if not template:
            _logger.error("Modèle d'email d'activation introuvable.")
            return False
        template.sudo().with_context(lang=user.lang or 'fr_FR').send_mail(
            user.id, force_send=True, raise_exception=False)
        user.write({
            'exocoms_activation_sent_date': fields.Datetime.now(),
            'exocoms_activation_email_count': user.exocoms_activation_email_count + 1,
        })
        _logger.info("Email d'activation envoyé à %s", user.login)
        return True

    def _exocoms_activate(self):
        """Consomme le jeton et réactive le compte."""
        self.ensure_one()
        user = self.sudo().with_context(active_test=False)
        user.write({
            'active': True,
            'exocoms_email_verified': True,
            'exocoms_activation_token': False,
            'exocoms_activation_url': False,
            'exocoms_activation_expiry': False,
            'exocoms_activation_date': fields.Datetime.now(),
        })
        if not user.partner_id.active:
            user.partner_id.sudo().write({'active': True})
        _logger.info("Compte portail activé : %s", user.login)
        return True

    @api.model
    def _exocoms_activate_from_token(self, token):
        """Retourne ``(état, utilisateur)`` pour un jeton donné.

        États possibles : ``done``, ``expired``, ``invalid``.
        """
        if not token:
            return 'invalid', self.browse()
        user = self.sudo().with_context(active_test=False).search(
            [('exocoms_activation_token', '=', token)], limit=1)
        if not user:
            return 'invalid', self.browse()
        if user.exocoms_activation_expiry \
                and user.exocoms_activation_expiry < fields.Datetime.now():
            return 'expired', user
        user._exocoms_activate()
        return 'done', user

    # ------------------------------------------------------------------
    # Actions back-office
    # ------------------------------------------------------------------
    def action_exocoms_resend_activation(self):
        self.ensure_one()
        self._exocoms_prepare_activation()
        self._exocoms_send_activation_email()
        return {
            'type': 'ir.actions.client',
            'tag': 'display_notification',
            'params': {
                'type': 'success',
                'title': _("Email d'activation renvoyé"),
                'message': _("Un nouveau lien a été envoyé à %s.", self.login),
                'sticky': False,
            },
        }

    def action_exocoms_force_activation(self):
        """Active manuellement un compte, sans passer par l'email."""
        for user in self:
            user._exocoms_activate()
        return True

    # ------------------------------------------------------------------
    # Purge
    # ------------------------------------------------------------------
    @api.model
    def _cron_exocoms_purge_pending(self):
        days = self._exocoms_get_int_param('purge_days')
        if days <= 0:
            return True
        limit_date = fields.Datetime.now() - timedelta(days=days)
        # Domaine volontairement restrictif : uniquement des comptes portail,
        # archivés, non vérifiés ET porteurs d'un jeton. Un utilisateur interne
        # archivé par un administrateur ne peut jamais être happé.
        users = self.sudo().with_context(active_test=False).search([
            ('exocoms_email_verified', '=', False),
            ('exocoms_activation_token', '!=', False),
            ('active', '=', False),
            ('share', '=', True),
            ('create_date', '<', limit_date),
        ])
        for user in users:
            login, partner = user.login, user.partner_id
            try:
                with self.env.cr.savepoint():
                    user.unlink()
                    if partner.exists() and not partner.user_ids:
                        partner.unlink()
                _logger.info("Inscription non activée purgée : %s", login)
            except Exception as exc:  # noqa: BLE001
                _logger.warning("Purge impossible pour %s : %s", login, exc)
        return True
