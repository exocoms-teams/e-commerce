# -*- coding: utf-8 -*-
"""Espace client (portail Odoo) : « Mes interventions »."""
from odoo import http
from odoo.http import request
from odoo.addons.portal.controllers.portal import CustomerPortal


class SinistrePortal(CustomerPortal):

    def _missions_client_domain(self):
        """Missions du client connecté (et de sa société s'il en a une)."""
        partner = request.env.user.partner_id
        return [('client_id', 'child_of', partner.commercial_partner_id.id)]

    def _prepare_home_portal_values(self, counters):
        """Compteur affiché sur la carte « Mes interventions » de /my."""
        values = super()._prepare_home_portal_values(counters)
        if 'intervention_count' in counters:
            values['intervention_count'] = request.env['sinistre.mission'].sudo().search_count(
                self._missions_client_domain()
            )
        return values

    @http.route('/my/interventions', type='http', auth='user', website=True)
    def portal_my_interventions(self, **kw):
        missions = request.env['sinistre.mission'].sudo().search(
            self._missions_client_domain(), order='date_reception desc',
        )
        values = self._prepare_portal_layout_values()
        values.update({
            'missions': missions,
            'page_name': 'interventions',
        })
        return request.render('sinistre_services.portal_my_interventions', values)
