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
        reference = post.get('reference')
        tx = request.env['payment.transaction'].sudo().search(
            [('reference', '=', reference)], limit=1
        )
        if tx:
            tx._apply_updates(post)
        return request.redirect('/payment/status')
