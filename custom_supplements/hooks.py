from odoo import api, SUPERUSER_ID

def post_init_hook(cr, registry):
    env = api.Environment(cr, SUPERUSER_ID, {})

    non_supplements = env["product.template"].search([
        ("is_supplement", "=", False),
    ])

    non_supplements.write({
        "is_published": False,
    })