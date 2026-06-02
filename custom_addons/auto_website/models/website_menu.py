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

    @api.model
    def _auto_website_normalize_navigation(self):
        menu_labels = {
            "/cars/home": "Accueil",
            "/cars": "Catalogue",
            "/brands": "Marques",
            "/my/favorites": "Favoris",
            "/cars/compare": "Comparateur",
        }
        languages = self.env["res.lang"].sudo().search([("active", "=", True)]).mapped("code")
        for url, label in menu_labels.items():
            menus = self.sudo().search([("url", "=", url)])
            for menu in menus:
                menu.sudo().write({"name": label})
                for lang in languages:
                    menu.with_context(lang=lang).sudo().write({"name": label})

        websites = self.env["website"].sudo().search([("name", "in", ["My Website", "Mon site web"])])
        for website in websites:
            website.sudo().write({"name": "EXOCOMS Voitures"})
            for lang in languages:
                website.with_context(lang=lang).sudo().write({"name": "EXOCOMS Voitures"})
        return True

    @api.model
    def _auto_website_update_contact_page(self):
        label = "Contact"
        meta_description = (
            "Coordonnées EXOCOMS Group : 58 rue de Monceau, 75008 Paris, "
            "+33 (0)1 84 79 37 55, contact@exocoms.fr."
        )
        languages = self.env["res.lang"].sudo().search([("active", "=", True)]).mapped("code")

        pages = self.env["website.page"].sudo().search([("url", "=", "/contactus")])
        values = {"name": label}
        if "website_meta_title" in self.env["website.page"]._fields:
            values["website_meta_title"] = "Contact EXOCOMS Group"
        if "website_meta_description" in self.env["website.page"]._fields:
            values["website_meta_description"] = meta_description
        for page in pages:
            page.sudo().write(values)
            for lang in languages:
                page.with_context(lang=lang).sudo().write(values)

        contact_view = self.env.ref("website.contactus", raise_if_not_found=False)
        if contact_view:
            contact_view.sudo().write({"name": "Contact EXOCOMS Group"})
            for lang in languages:
                contact_view.with_context(lang=lang).sudo().write({"name": "Contact EXOCOMS Group"})
        return True
