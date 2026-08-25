from odoo import api, SUPERUSER_ID
import logging

_logger = logging.getLogger(__name__)

def demo_purge(env):
    _logger.warning("purging demo-data")

    non_supplements = env["product.template"].search([
        ("is_supplement", "=", False),
    ])
    for product in non_supplements:
        _logger.info(" unlisting %s",product.name)
        product.write({
            "is_published": False,
            "active":False
        })
        