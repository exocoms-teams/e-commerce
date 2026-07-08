from . import models
from . import controllers


def post_init_hook(env):
    """Ajoute le menu infogerance détaillée"""
    from odoo.addons.website.models.website import Menu

    website = env['website'].search([('name', '=', 'Exocoms Group')], limit=1)
    if not website:
        website = env['website'].search([], limit=1)

    if not website:
        return

    parent_menu = env['website.menu'].search([
        ('url', '=', '/infogerance'),
        ('website_id', '=', website.id),
    ], limit=1)

    if parent_menu:
        existing = env['website.menu'].search([
            ('url', '=', '/infogerance/detail'),
            ('website_id', '=', website.id),
        ], limit=1)
        if not existing:
            env['website.menu'].create({
                'name': 'Détail & tarifs',
                'url': '/infogerance/detail',
                'website_id': website.id,
                'parent_id': parent_menu.id,
                'sequence': 20,
            })


def post_migrate_hook(env):
    post_init_hook(env)
