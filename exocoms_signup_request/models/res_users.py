# -*- coding: utf-8 -*-
import logging

from odoo import api, models

_logger = logging.getLogger(__name__)


class ResUsers(models.Model):
    _inherit = 'res.users'

    @api.model
    def signup(self, values, token=None):
        """Rattache le nouveau compte aux sociétés dont il a confirmé l'adresse.

        Le login étant unique sur toute la base, un client qui s'inscrit sur le
        site de la société A puis sur celui de la société B possède **un seul**
        compte. Sans rattachement explicite, il ne verrait dans son portail que
        les documents de la société d'origine, et ses commandes chez l'autre
        entité lui resteraient invisibles.

        Le parcours natif crée l'utilisateur avec la société courante. On se
        contente d'ajouter ici les sociétés issues des demandes confirmées pour
        cette adresse : jamais de retrait, et la société principale n'est pas
        modifiée.
        """
        result = super().signup(values, token)
        login = None
        if isinstance(result, (tuple, list)) and result:
            login = result[0]
        login = login or values.get('login')
        try:
            self._exocoms_sync_signup_companies(login)
        except Exception:  # noqa: BLE001 - ne doit jamais casser l'inscription
            _logger.exception(
                "Rattachement multi-société impossible pour %s", login)
        return result

    @api.model
    def _exocoms_sync_signup_companies(self, login):
        """Ajoute au compte les sociétés de ses demandes confirmées."""
        if not login:
            return False
        Requests = self.env['exocoms.signup.request'].sudo()
        Users = self.sudo().with_context(active_test=False)

        user = Users.search(
            Users._get_login_domain(login), order=Users._get_login_order(), limit=1)
        if not user or not user.share:
            # Rattachement réservé aux comptes portail : on ne touche jamais
            # aux droits d'un utilisateur interne.
            return False

        requests = Requests.search([
            ('email', '=ilike', Requests._ilike_escape(login)),
            ('state', '=', 'confirmed'),
            ('company_id', '!=', False),
        ])
        companies = requests.mapped('company_id')
        missing = companies - user.company_ids
        if not missing:
            return False

        user.write({'company_ids': [(4, company.id) for company in missing]})
        _logger.info(
            "Compte portail %s rattaché à : %s",
            login, ', '.join(missing.mapped('name')))
        return True
