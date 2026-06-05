from . import models
from . import controllers


def post_init_hook(env):
    """Assigne le template home à la page d'accueil du site"""
    website = env['website'].search([], limit=1)
    if website:
        # Cherche la vue home de notre thème
        view = env['ir.ui.view'].search([
            ('key', '=', 'monetique_theme.home'),
        ], limit=1)
        if view:
            # Assigne comme homepage
            website.homepage_id = view
