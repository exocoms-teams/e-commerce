# -*- coding: utf-8 -*-
import logging
import pprint

from odoo import http
from odoo.http import request

_logger = logging.getLogger(__name__)


class MandatAdministratifController(http.Controller):
    _process_url = '/payment/mandat_administratif/process'

    @http.route(_process_url, type='http', auth='public', methods=['POST'],
                csrf=False)
    def mandat_administratif_process(self, **post):
        """Traiter les données postées par le formulaire de redirection et
        mettre la transaction en attente (règlement via Chorus Pro)."""
        _logger.info(
            "Mandat administratif : données reçues :\n%s", pprint.pformat(post)
        )

        # Récupérer la transaction par sa référence pour compléter les données
        reference = post.get('reference')
        if reference:
            tx = request.env['payment.transaction'].sudo().search([('reference', '=', reference)], limit=1)
            if tx:
                post.update({
                    'amount': tx.amount,
                    'currency': tx.currency_id.name,
                })

        request.env['payment.transaction'].sudo()._process(
            'mandat_administratif', post
        )
        return request.redirect('/payment/status')
