from odoo import api, SUPERUSER_ID
import logging

_logger = logging.getLogger(__name__)

def post_init_hook(cr, registry):
    _logger.warning("purging demo-data")
    env = api.Environment(cr, SUPERUSER_ID, {})

    non_supplements = env["product.template"].search([
        ("is_supplement", "=", False),
    ])

    non_supplements.write({
        "is_published": False,
    })