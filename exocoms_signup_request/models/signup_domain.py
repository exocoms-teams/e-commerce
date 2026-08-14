# -*- coding: utf-8 -*-
from odoo import api, fields, models
from odoo.exceptions import ValidationError


class ExocomsSignupDomain(models.Model):
    _name = 'exocoms.signup.domain'
    _description = "Domaine email d'inscription"
    _order = 'kind, name'

    name = fields.Char(
        string="Domaine", required=True, index=True,
        help="Domaine sans le @, par exemple : yopmail.com")
    kind = fields.Selection(
        [('blocked', "Refusé"), ('allowed', "Autorisé")],
        string="Type", required=True, default='blocked',
        help="Refusé : les demandes provenant de ce domaine sont rejetées.\n"
             "Autorisé : utilisé uniquement si la restriction par liste "
             "blanche est activée dans les réglages.")
    active = fields.Boolean(string="Actif", default=True)
    note = fields.Char(string="Commentaire")

    _sql_constraints = [
        ('name_kind_uniq', 'unique(name, kind)',
         "Ce domaine figure déjà dans cette liste."),
    ]

    @api.constrains('name')
    def _check_name(self):
        for record in self:
            value = (record.name or '').strip()
            if not value or '@' in value or '.' not in value or ' ' in value:
                raise ValidationError(
                    "« %s » n'est pas un domaine valide. Saisissez le domaine "
                    "seul, sans le @ (exemple : yopmail.com)." % record.name)

    @staticmethod
    def _normalize(value):
        return (value or '').strip().lower().lstrip('@')

    @api.model_create_multi
    def create(self, vals_list):
        for vals in vals_list:
            if vals.get('name'):
                vals['name'] = self._normalize(vals['name'])
        return super().create(vals_list)

    def write(self, vals):
        if vals.get('name'):
            vals['name'] = self._normalize(vals['name'])
        return super().write(vals)

    @api.model
    def _exocoms_domain_set(self, kind):
        """Ensemble des domaines actifs pour un type donné."""
        records = self.sudo().search([('kind', '=', kind)])
        return {record.name for record in records if record.name}
