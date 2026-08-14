# -*- coding: utf-8 -*-
import secrets

from odoo import api, SUPERUSER_ID

from . import models
from . import wizard
from . import controllers


def post_init_hook(env):
    """Génère un sel de pseudonymisation propre à la base."""
    params = env["ir.config_parameter"].sudo()
    if not params.get_param("exocoms_rgpd.hash_salt"):
        params.set_param("exocoms_rgpd.hash_salt", secrets.token_urlsafe(32))
    if not params.get_param("exocoms_rgpd.audit_retention_months"):
        params.set_param("exocoms_rgpd.audit_retention_months", "12")
