# -*- coding: utf-8 -*-
import logging

_logger = logging.getLogger(__name__)


def post_init_hook(env):
    """Initialise les paramètres et amorce la marque avec l'identité société."""
    icp = env["ir.config_parameter"].sudo()
    if not icp.get_param("exocoms_debranding.enabled"):
        icp.set_param("exocoms_debranding.enabled", "True")

    for company in env["res.company"].sudo().search([]):
        values = {}
        if not company.debrand_brand_name:
            values["debrand_brand_name"] = company.name
        if not company.debrand_brand_url and company.website:
            values["debrand_brand_url"] = company.website
        if values:
            company.write(values)

    env.registry.clear_cache()
    _logger.info("EXOCOMS marque blanche activée (rendu QWeb personnalisé).")
