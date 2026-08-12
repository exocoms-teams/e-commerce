/** @odoo-module **/

import { registry } from "@web/core/registry";
import { session } from "@web/session";

if (session.exocoms_debranding) {
    // 1. Retrait des entrées Odoo du menu utilisateur (Documentation, Support, Compte).
    const userMenuRegistry = registry.category("user_menuitems");
    for (const key of ["documentation", "support", "odoo_account"]) {
        if (userMenuRegistry.contains(key)) {
            userMenuRegistry.remove(key);
        }
    }

    // 2. Remplacement de "Odoo" par le nom de la société dans le titre de l'onglet.
    registry.category("services").add("exocoms_debranding", {
        dependencies: ["title"],
        start(env, { title }) {
            title.setParts({ zopenerp: session.exocoms_brand_name || "EXOCOMS" });
        },
    });
}
