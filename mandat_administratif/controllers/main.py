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
        """Traiter les données postées et mettre la transaction en attente."""
        _logger.info("Mandat administratif : données reçues :\n%s", pprint.pformat(post))

        # Odoo attend une référence dans le dictionnaire de notification
        if 'reference' in post:
            request.env['payment.transaction'].sudo()._handle_notification_data(
                'mandat_administratif', post
            )

        return request.redirect('/payment/status')
