import base64

from odoo import api, models
from odoo.tools import file_open


class WebsiteMenu(models.Model):
    _inherit = "website.menu"

    @api.model
    def _auto_website_remove_obsolete_qweb_overrides(self):
        override_names = [
            "odoo19_web_layout_t_out",
            "odoo19_portal_language_selector_t_out",
            "odoo19_portal_user_dropdown_t_out",
            "odoo19_banner_categories_t_out",
            "footer_copyright_exocoms",
        ]
        external_ids = self.env["ir.model.data"].sudo().search(
            [
                ("module", "=", "auto_website"),
                ("name", "in", override_names),
            ]
        )
        view_ids = [
            external_id.res_id
            for external_id in external_ids
            if external_id.model == "ir.ui.view" and external_id.res_id
        ]
        if view_ids:
            self.env["ir.ui.view"].sudo().browse(view_ids).exists().unlink()
        external_ids.exists().unlink()
        return True

    @api.model
    def _auto_website_page_title(self, key):
        titles = {
            "contact": self.env._("Contacter EXOCOMS"),
            "cart": self.env._("Panier automobile"),
        }
        return titles.get(key, "")

    @api.model
    def _auto_website_configure_languages(self):
        language_specs = [
            {
                "code": "fr_FR",
                "name": "Français",
                "url_code": "fr",
                "direction": "ltr",
            },
            {
                "code": "en_GB",
                "name": "English",
                "url_code": "en",
                "direction": "ltr",
            },
            {
                "code": "ar_001",
                "name": "العربي",
                "url_code": "ar",
                "direction": "rtl",
            },
        ]
        Lang = self.env["res.lang"].sudo().with_context(active_test=False)
        languages = self.env["res.lang"].sudo()
        default_lang = self.env["res.lang"].sudo()

        for spec in language_specs:
            if "url_code" in Lang._fields:
                conflicting_langs = Lang.search(
                    [
                        ("url_code", "=", spec["url_code"]),
                        ("code", "!=", spec["code"]),
                    ]
                )
                for conflicting_lang in conflicting_langs:
                    conflicting_lang.write(
                        {"url_code": conflicting_lang.code.lower().replace("_", "-")}
                    )
            lang = Lang.search([("code", "=", spec["code"])], limit=1)
            if not lang:
                lang = Lang._create_lang(spec["code"], spec["name"])
            values = {
                "name": spec["name"],
                "active": True,
            }
            if "url_code" in Lang._fields:
                values["url_code"] = spec["url_code"]
            if "direction" in Lang._fields:
                values["direction"] = spec["direction"]
            lang.write(values)
            languages |= lang
            if spec["code"] == "fr_FR":
                default_lang = lang

        websites = self.env["website"].sudo().search([])
        for website in websites:
            values = {
                "language_ids": [(6, 0, languages.ids)],
            }
            if default_lang:
                values["default_lang_id"] = default_lang.id
            website.write(values)

        # Activating a language alone does not load translations for modules
        # that were already installed before this website module.
        installer_values = {
            "lang_ids": [(6, 0, languages.ids)],
            "overwrite": True,
        }
        language_installer = self.env["base.language.install"].sudo()
        if "website_ids" in language_installer._fields:
            installer_values["website_ids"] = [(6, 0, websites.ids)]
        language_installer.create(installer_values).lang_install()
        return True

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
            "/cars/home": {
                "fr_FR": "Accueil",
                "en_GB": "Home",
                "ar_001": "الرئيسية",
            },
            "/cars": {
                "fr_FR": "Catalogue",
                "en_GB": "Catalog",
                "ar_001": "الكتالوج",
            },
            "/brands": {
                "fr_FR": "Marques",
                "en_GB": "Brands",
                "ar_001": "العلامات التجارية",
            },
            "/my/favorites": {
                "fr_FR": "Favoris",
                "en_GB": "Favorites",
                "ar_001": "المفضلة",
            },
            "/cars/compare": {
                "fr_FR": "Comparateur",
                "en_GB": "Compare",
                "ar_001": "مقارنة",
            },
            "/contactus": {
                "fr_FR": "Contact",
                "en_GB": "Contact",
                "ar_001": "اتصل بنا",
            },
        }
        for url, labels in menu_labels.items():
            menus = self.sudo().search([("url", "=", url)])
            menus.write({"name": labels["fr_FR"]})
            for lang_code, label in labels.items():
                menus.with_context(lang=lang_code).write({"name": label})

        websites = self.env["website"].sudo().search(
            [("name", "in", ["My Website", "Mon site web", "EXOCOMS Voitures"])]
        )
        for website in websites:
            website.sudo().write({"name": "EXOCOMS Voitures"})
        return True

    @api.model
    def _auto_website_set_homepage(self):
        websites = self.env["website"].sudo().search(
            [("name", "in", ["My Website", "Mon site web", "EXOCOMS Voitures"])]
        )
        if not websites:
            websites = self.env["website"].sudo().search([])
        if "homepage_url" in self.env["website"]._fields:
            websites.write({"homepage_url": "/cars/home"})
        return True

    @api.model
    def _auto_website_update_company_contact(self):
        france = self.env.ref("base.fr", raise_if_not_found=False)
        company_values = {
            "name": "EXOCOMS Group",
            "phone": "+33 (0)1 84 79 37 55",
            "email": "contact@exocoms.fr",
            "street": "58 rue de Monceau",
            "zip": "75008",
            "city": "Paris",
            "website": "https://www.exocoms.fr/",
        }
        if france:
            company_values["country_id"] = france.id

        websites = self.env["website"].sudo().search(
            [("name", "in", ["My Website", "Mon site web", "EXOCOMS Voitures"])]
        )
        if not websites:
            websites = self.env["website"].sudo().search([], limit=1)

        companies = websites.mapped("company_id")
        if not companies:
            companies = self.env.company
        companies.sudo().write(company_values)
        return True

    @api.model
    def _auto_website_update_branding(self):
        with file_open("auto_website/static/src/img/exocoms-logo.png", "rb") as logo_file:
            logo = base64.b64encode(logo_file.read())

        websites = self.env["website"].sudo().search(
            [("name", "in", ["My Website", "Mon site web", "EXOCOMS Voitures"])]
        )
        if not websites:
            websites = self.env["website"].sudo().search([], limit=1)
        websites.sudo().write({"logo": logo})
        return True

    @api.model
    def _auto_website_replace_default_header_phone(self):
        replacements = {
            "tel:+1 555-555-5556": "tel:+33184793755",
            "+1 555-555-5556": "+33 (0)1 84 79 37 55",
        }
        views = self.env["ir.ui.view"].sudo().search([("arch_db", "ilike", "+1 555-555-5556")])
        for view in views:
            arch = view.arch_db or ""
            updated_arch = arch
            for old_value, new_value in replacements.items():
                updated_arch = updated_arch.replace(old_value, new_value)
            if updated_arch != arch:
                view.sudo().write({"arch_db": updated_arch})
        return True

    @api.model
    def _auto_website_update_contact_page(self):
        pages = self.env["website.page"].sudo().search([("url", "=", "/contactus")])
        translations = {
            "fr_FR": {
                "name": "Contact",
                "website_meta_title": "Contact EXOCOMS Group",
                "website_meta_description": (
                    "Coordonnées EXOCOMS Group : 58 rue de Monceau, 75008 Paris, "
                    "+33 (0)1 84 79 37 55, contact@exocoms.fr."
                ),
            },
            "en_GB": {
                "name": "Contact",
                "website_meta_title": "Contact EXOCOMS Group",
                "website_meta_description": (
                    "EXOCOMS Group contact details: 58 rue de Monceau, 75008 Paris, "
                    "+33 (0)1 84 79 37 55, contact@exocoms.fr."
                ),
            },
            "ar_001": {
                "name": "اتصل بنا",
                "website_meta_title": "التواصل مع مجموعة EXOCOMS",
                "website_meta_description": (
                    "بيانات التواصل مع مجموعة EXOCOMS: 58 rue de Monceau، 75008 Paris، "
                    "+33 (0)1 84 79 37 55، contact@exocoms.fr."
                ),
            },
        }
        available_fields = self.env["website.page"]._fields
        for page in pages:
            page.write({"name": translations["fr_FR"]["name"]})
            for lang_code, translated_values in translations.items():
                values = {
                    field_name: value
                    for field_name, value in translated_values.items()
                    if field_name in available_fields
                }
                page.with_context(lang=lang_code).write(values)

        contact_view = self.env.ref("website.contactus", raise_if_not_found=False)
        if contact_view:
            contact_view.sudo().write({"name": "Contact EXOCOMS Group"})
        return True
