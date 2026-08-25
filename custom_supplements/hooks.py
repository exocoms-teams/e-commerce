from odoo import api, SUPERUSER_ID
import logging

_logger = logging.getLogger(__name__)

def demo_purge(env):
    _logger.warning("purging demo-data")

    non_supplements = env["product.product"].search([
        # ("is_supplement", "=", False),
        (True,"=",True)
    ])
    for product in non_supplements:
        _logger.info(" Product : %s | Supplement : %s",product.name, product.is_supplement)
        # product.write({
        #     "is_published": False,
        #     "active":False
        # })
