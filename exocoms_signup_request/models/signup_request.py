# -*- coding: utf-8 -*-
import hashlib
import hmac
import logging
import re
import secrets
from datetime import timedelta

from odoo import _, api, fields, models
from odoo.exceptions import UserError

_logger = logging.getLogger(__name__)

PREFIX = 'exocoms_signup_request.'

DEFAULTS = {
    'token_ttl_hours': 24,
    'resend_interval': 120,
    'max_resend': 5,
    'keep_expired_days': 7,
    'keep_confirmed_days': 30,
    'keep_rejected_days': 3,
    'max_per_ip': 5,
    'ip_window_minutes': 60,
}

# Volontairement permissif : écarter les saisies manifestement erronées, pas
# réimplémenter la RFC 5322.
EMAIL_RE = re.compile(r"^[^@\s]+@[^@\s]+\.[A-Za-z]{2,}$")


class ExocomsSignupRequest(models.Model):
    _name = 'exocoms.signup.request'
    _description = "Demande d'inscription portail"
    _order = 'create_date desc'
    _rec_name = 'email'

    email = fields.Char(string="Adresse email", required=True, index=True, readonly=True)
    name = fields.Char(string="Nom", readonly=True)
    lang = fields.Char(string="Langue", readonly=True)

    token = fields.Char(string="Jeton", index=True, copy=False, groups='base.group_system')
    confirm_url = fields.Char(string="Lien de confirmation", copy=False,
                              groups='base.group_system')
    expiry = fields.Datetime(string="Expiration du lien", readonly=True)

    state = fields.Selection(
        [('pending', "En attente de confirmation"),
         ('confirmed', "Confirmée"),
         ('rejected', "Refusée"),
         ('expired', "Expirée")],
        string="État", default='pending', required=True, index=True, readonly=True)
    reject_reason = fields.Char(string="Motif du refus", readonly=True)

    sent_date = fields.Datetime(string="Dernier envoi", readonly=True)
    email_count = fields.Integer(string="Emails envoyés", default=0, readonly=True)
    confirmed_date = fields.Datetime(string="Date de confirmation", readonly=True)

    ip_hash = fields.Char(
        string="Empreinte d'origine", index=True, readonly=True,
        groups='base.group_system',
        help="Empreinte HMAC de l'adresse IP d'origine. L'adresse elle-même "
             "n'est jamais enregistrée : l'empreinte ne sert qu'à plafonner le "
             "nombre de demandes provenant d'une même source, et disparaît "
             "avec la demande lors de la purge.")
    website_id = fields.Many2one('website', string="Site web", readonly=True)
    company_id = fields.Many2one('res.company', string="Société", readonly=True)
    partner_id = fields.Many2one('res.partner', string="Contact créé",
                                 readonly=True, ondelete='set null')

    _sql_constraints = [
        ('token_uniq', 'unique(token)', "Jeton déjà utilisé."),
    ]

    # ------------------------------------------------------------------
    # Paramétrage
    # ------------------------------------------------------------------
    @api.model
    def _get_int_param(self, key):
        raw = self.env['ir.config_parameter'].sudo().get_param(
            PREFIX + key, DEFAULTS.get(key, 0))
        try:
            return int(raw)
        except (TypeError, ValueError):
            return DEFAULTS.get(key, 0)

    @api.model
    def _get_bool_param(self, key, default=True):
        raw = self.env['ir.config_parameter'].sudo().get_param(PREFIX + key)
        if raw is None or raw is False:
            return default
        return str(raw).strip().lower() not in ('', '0', 'false')

    # ------------------------------------------------------------------
    # Vérification de l'adresse
    # ------------------------------------------------------------------
    @api.model
    def _check_email(self, email):
        """Valide une adresse et la retourne normalisée.

        Lève une ``UserError`` dont le message s'affiche tel quel sur le
        formulaire public.
        """
        address = (email or '').strip().lower()
        if not EMAIL_RE.match(address):
            raise UserError(_("Cette adresse email n'est pas valide."))

        domain = address.rsplit('@', 1)[-1]
        Domains = self.env['exocoms.signup.domain']

        if self._get_bool_param('block_disposable', True):
            if domain in Domains._exocoms_domain_set('blocked'):
                raise UserError(_(
                    "Les adresses email jetables ne sont pas acceptées. "
                    "Merci d'utiliser une adresse professionnelle ou "
                    "personnelle permanente."))

        if self._get_bool_param('restrict_allowed', False):
            allowed = Domains._exocoms_domain_set('allowed')
            if allowed and domain not in allowed:
                raise UserError(_(
                    "Les inscriptions sont réservées à une liste de domaines "
                    "autorisés. Merci de contacter notre support."))

        if self._get_bool_param('check_mx', True):
            self._check_mx(domain)

        return address

    @api.model
    def _check_mx(self, domain):
        """Vérifie que le domaine peut recevoir du courrier.

        Dégradation propre : sans ``dnspython``, ou en cas d'incident réseau,
        l'inscription passe. On ne refuse que sur une réponse DNS explicitement
        négative — un problème d'infrastructure ne doit pas bloquer une vente.
        """
        try:
            import dns.resolver  # noqa: PLC0415
        except ImportError:
            _logger.info("dnspython absent : contrôle DNS ignoré (%s)", domain)
            return True

        resolver = dns.resolver.Resolver()
        resolver.timeout = 5
        resolver.lifetime = 5
        try:
            if resolver.resolve(domain, 'MX'):
                return True
        except (dns.resolver.NXDOMAIN, dns.resolver.NoAnswer):
            # Un domaine sans MX mais avec un A reste un destinataire valide.
            try:
                if resolver.resolve(domain, 'A'):
                    return True
            except Exception:  # noqa: BLE001
                pass
            raise UserError(_(
                "Le domaine « %s » ne semble pas pouvoir recevoir d'emails. "
                "Merci de vérifier votre adresse.", domain))
        except Exception as exc:  # noqa: BLE001
            _logger.info("Contrôle DNS indisponible pour %s : %s", domain, exc)
            return True
        return True

    # ------------------------------------------------------------------
    # Création et envoi
    # ------------------------------------------------------------------
    @staticmethod
    def _ilike_escape(value):
        """Neutralise les jokers SQL d'une adresse email.

        ``=ilike`` interprète ``_`` et ``%`` comme des jokers. Or ``_`` est
        courant dans les adresses : sans échappement, « jean_dupont@x.fr »
        correspondrait aussi à « jeanXdupont@x.fr ». Sur la recherche de
        contact, cela ouvrirait une prise de contrôle de compte.
        """
        return (value or '').replace('\\', '\\\\').replace('_', '\\_').replace('%', '\\%')

    @api.model
    def _hash_ip(self, ip_address):
        """Empreinte non réversible d'une adresse IP.

        L'adresse n'est jamais stockée : seul un HMAC-SHA256 tronqué, calculé
        avec le secret de la base, sert au plafonnement. Le sel étant propre à
        l'instance, l'empreinte est inexploitable en dehors de celle-ci.
        """
        address = (ip_address or '').strip()
        if not address:
            return False
        secret = self.env['ir.config_parameter'].sudo().get_param(
            'database.secret') or 'exocoms'
        digest = hmac.new(secret.encode(), address.encode(), hashlib.sha256)
        return digest.hexdigest()[:32]

    @api.model
    def _check_source_quota(self, ip_hash):
        """Plafonne le nombre de demandes issues d'une même origine.

        Sans cela, le formulaire permettrait à un robot de déposer des milliers
        d'adresses différentes : autant d'emails envoyés à des tiers qui n'ont
        rien demandé. Le message reste volontairement neutre pour ne rien
        révéler du seuil appliqué.
        """
        if not ip_hash:
            return True
        max_per_ip = self._get_int_param('max_per_ip')
        window = self._get_int_param('ip_window_minutes')
        if max_per_ip <= 0 or window <= 0:
            return True
        since = fields.Datetime.now() - timedelta(minutes=window)
        count = self.sudo().search_count([
            ('ip_hash', '=', ip_hash),
            ('create_date', '>', since),
        ])
        if count >= max_per_ip:
            _logger.warning(
                "Quota d'inscription atteint pour une origine (%s demandes "
                "en %s minutes)", count, window)
            raise UserError(_(
                "Trop de demandes ont été envoyées depuis cette connexion. "
                "Merci de réessayer plus tard ou de contacter notre support."))
        return True

    @api.model
    def _find_pending(self, email):
        if not email:
            return self.browse()
        return self.sudo().search(
            [('email', '=ilike', self._ilike_escape(email.strip())),
             ('state', '=', 'pending')],
            limit=1)

    @api.model
    def _submit(self, email, name=None, base_url=None, website=None, lang=None,
                ip_address=None):
        """Point d'entrée du formulaire public.

        Retourne la demande créée ou relancée. Ne crée **aucun** utilisateur ni
        contact : seule une ligne de cette table est écrite.
        """
        ip_hash = self._hash_ip(ip_address)
        # Le quota d'origine passe avant la validation de l'adresse : un robot
        # ne doit pas pouvoir sonder les règles de filtrage sans limite.
        self._check_source_quota(ip_hash)

        try:
            address = self._check_email(email)
        except UserError as exc:
            # L'état « refusée » alimente le diagnostic (« pourquoi mon client
            # n'arrive-t-il pas à s'inscrire ? ») et la durée de conservation
            # correspondante dans les réglages. Sans cette trace, l'option
            # serait sans objet.
            self._log_rejection(email, exc.args[0], ip_hash=ip_hash)
            raise
        website = website or self.env['website'].browse()
        company = website.company_id or self.env.company

        pending = self._find_pending(address)
        if pending:
            # Le nom soumis est ignoré : un tiers connaissant l'adresse ne doit
            # pas pouvoir modifier une demande en cours. Les quotas s'appliquent,
            # faute de quoi le formulaire deviendrait un outil d'envoi massif.
            try:
                pending._check_resend_allowed()
                pending._refresh_token(base_url=base_url)
                pending._send_confirmation_email()
            except UserError as exc:
                _logger.info("Relance ignorée pour %s : %s", address, exc)
            return pending

        request_rec = self.sudo().create({
            'email': address,
            'name': (name or '').strip() or False,
            'lang': lang or self.env.context.get('lang') or 'fr_FR',
            'website_id': website.id or False,
            'company_id': company.id,
            'ip_hash': ip_hash,
        })
        request_rec._refresh_token(base_url=base_url)
        request_rec._send_confirmation_email()
        return request_rec

    @api.model
    def _log_rejection(self, email, reason, ip_hash=False):
        """Trace un refus, au plus une fois par adresse et par jour.

        La déduplication évite qu'un robot ne remplisse la table en répétant la
        même adresse invalide.
        """
        address = (email or '').strip().lower()[:254]
        if not address:
            return self.browse()
        recent = self.sudo().search([
            ('email', '=ilike', self._ilike_escape(address)),
            ('state', '=', 'rejected'),
            ('create_date', '>', fields.Datetime.now() - timedelta(days=1)),
        ], limit=1)
        if recent:
            return recent
        return self.sudo().create({
            'email': address,
            'state': 'rejected',
            'reject_reason': (reason or '')[:255],
            'company_id': self.env.company.id,
            'ip_hash': ip_hash,
        })

    def _default_base_url(self):
        self.ensure_one()
        website = self.website_id or self.env['website'].sudo().search(
            [('company_id', '=', self.company_id.id)], limit=1)
        if website and website.domain:
            domain = website.domain.strip()
            if not domain.startswith(('http://', 'https://')):
                domain = 'https://%s' % domain
            return domain
        return self.env['ir.config_parameter'].sudo().get_param('web.base.url') or ''

    def _refresh_token(self, base_url=None):
        """Génère un jeton neuf et l'URL de confirmation associée."""
        self.ensure_one()
        token = secrets.token_urlsafe(32)
        root = (base_url or self._default_base_url()).rstrip('/')
        self.sudo().write({
            'token': token,
            'confirm_url': '%s/signup/confirm/%s' % (root, token),
            'expiry': fields.Datetime.now() + timedelta(
                hours=self._get_int_param('token_ttl_hours')),
            'state': 'pending',
        })
        return token

    def _check_resend_allowed(self):
        """Contrôle de fréquence et de volume.

        Appelé **avant** ``_refresh_token()`` : un renvoi refusé ne doit pas
        invalider le lien déjà reçu.
        """
        self.ensure_one()
        interval = self._get_int_param('resend_interval')
        max_resend = self._get_int_param('max_resend')

        if interval and self.sent_date:
            elapsed = (fields.Datetime.now() - self.sent_date).total_seconds()
            if elapsed < interval:
                raise UserError(_(
                    "Un email vient d'être envoyé. Merci de patienter %s "
                    "secondes avant d'en demander un nouveau.",
                    int(interval - elapsed)))

        if max_resend and self.email_count >= max_resend:
            raise UserError(_(
                "Le nombre maximum d'emails a été atteint pour cette adresse. "
                "Merci de contacter notre support."))
        return True

    def _send_confirmation_email(self):
        self.ensure_one()
        record = self.sudo()
        template = self.env.ref(
            'exocoms_signup_request.mail_template_signup_confirm',
            raise_if_not_found=False)
        if not template:
            _logger.error("Modèle d'email de confirmation introuvable.")
            return False
        template.sudo().with_context(lang=record.lang or 'fr_FR').send_mail(
            record.id, force_send=True, raise_exception=False)
        record.write({
            'sent_date': fields.Datetime.now(),
            'email_count': record.email_count + 1,
        })
        _logger.info("Email de confirmation envoyé à %s", record.email)
        return True

    def action_resend(self):
        """Bouton back-office."""
        self.ensure_one()
        if self.state == 'confirmed':
            raise UserError(_(
                "Cette demande est déjà confirmée. Utilisez la "
                "réinitialisation de mot de passe sur le compte concerné."))
        self._refresh_token()
        self._send_confirmation_email()
        return {
            'type': 'ir.actions.client',
            'tag': 'display_notification',
            'params': {
                'type': 'success',
                'title': _("Email renvoyé"),
                'message': _("Un nouveau lien a été envoyé à %s.", self.email),
                'sticky': False,
            },
        }

    # ------------------------------------------------------------------
    # Confirmation
    # ------------------------------------------------------------------
    @api.model
    def _confirm_token(self, token):
        """Consomme un jeton.

        Retourne ``(état, demande)`` où l'état vaut ``done``, ``expired`` ou
        ``invalid``. En cas de succès, le contact est créé et un jeton
        d'invitation Odoo est préparé sur celui-ci : la suite du parcours est
        entièrement native.
        """
        if not token:
            return 'invalid', self.browse()
        record = self.sudo().search([('token', '=', token)], limit=1)
        if not record or record.state != 'pending':
            return 'invalid', self.browse()
        if record.expiry and record.expiry < fields.Datetime.now():
            record.write({'state': 'expired'})
            return 'expired', record
        record._create_partner_and_prepare_signup()
        return 'done', record

    def _create_partner_and_prepare_signup(self):
        """Crée le contact et prépare le jeton d'invitation natif."""
        self.ensure_one()
        record = self.sudo()
        Partner = self.env['res.partner'].sudo()

        partner = Partner.with_context(active_test=False).search(
            [('email', '=ilike', self._ilike_escape(record.email))], limit=1)
        if not partner:
            partner = Partner.create({
                'name': record.name or record.email,
                'email': record.email,
                'lang': record.lang or self.env.context.get('lang') or 'fr_FR',
                'company_id': False,
            })
        elif not partner.active:
            partner.write({'active': True})

        # Jeton d'invitation Odoo : c'est lui qui autorisera la page native
        # /web/signup?token=... à créer l'utilisateur et à ouvrir la session.
        partner.signup_prepare(
            signup_type='signup',
            expiration=fields.Datetime.now() + timedelta(
                hours=self._get_int_param('token_ttl_hours')))

        record.write({
            'state': 'confirmed',
            'confirmed_date': fields.Datetime.now(),
            'partner_id': partner.id,
            'token': False,
            'confirm_url': False,
        })
        _logger.info("Demande confirmée, contact créé : %s", record.email)
        return partner

    def _reject(self, reason):
        self.ensure_one()
        self.sudo().write({
            'state': 'rejected',
            'reject_reason': reason,
            'token': False,
            'confirm_url': False,
        })
        return True

    # ------------------------------------------------------------------
    # Purge
    # ------------------------------------------------------------------
    @api.model
    def _cron_purge(self):
        """Nettoie cette table, et elle seule.

        Aucun ``res.users`` ni ``res.partner`` n'est touché : le pire scénario
        est la suppression d'une demande d'inscription non confirmée.
        """
        now = fields.Datetime.now()
        Requests = self.sudo()

        # Les demandes dont le lien a expiré passent d'abord à l'état expiré,
        # ce qui les rend visibles en back-office avant leur suppression.
        stale = Requests.search([
            ('state', '=', 'pending'),
            ('expiry', '<', now),
        ])
        if stale:
            stale.write({'state': 'expired', 'token': False, 'confirm_url': False})
            _logger.info("%s demande(s) marquée(s) expirée(s)", len(stale))

        plan = [
            ('expired', self._get_int_param('keep_expired_days')),
            ('confirmed', self._get_int_param('keep_confirmed_days')),
            ('rejected', self._get_int_param('keep_rejected_days')),
        ]
        for state, days in plan:
            if days <= 0:
                continue
            records = Requests.search([
                ('state', '=', state),
                ('create_date', '<', now - timedelta(days=days)),
            ])
            for record in records:
                email = record.email
                try:
                    with self.env.cr.savepoint():
                        record.unlink()
                except Exception as exc:  # noqa: BLE001
                    _logger.warning("Purge impossible pour %s : %s", email, exc)
            if records:
                _logger.info("Purge : %s demande(s) « %s » traitée(s)",
                             len(records), state)
        return True
