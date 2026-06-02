from odoo import api, models


class WebsiteMenu(models.Model):
    _inherit = "website.menu"

    @api.model
    def _auto_website_remove_default_navigation(self):
        self.env.cr.execute(
            "SELECT id FROM website_menu WHERE url IN %s",
            [("/", "/shop")],
        )
        menu_ids = [row[0] for row in self.env.cr.fetchall()]
        if menu_ids:
            self.browse(menu_ids).sudo().unlink()
        return True
