/** @odoo-module **/

import { patch } from "@web/core/utils/patch";
import { registry } from "@web/core/registry";
import { session } from "@web/session";
import { _t } from "@web/core/l10n/translation";
import { WebClient } from "@web/webclient/webclient";
import * as errorDialogs from "@web/core/errors/error_dialogs";

const branding = session.debranding || {};
const BRAND = branding.name || "";

/* ------------------------------------------------------------------
 * 1. Titre de l'onglet navigateur
 * Le webclient pose systématiquement la partie "zopenerp" = "Odoo".
 * ------------------------------------------------------------------ */
patch(WebClient.prototype, {
    setup() {
        super.setup();
        // null supprime la partie du titre.
        this.title.setParts({ zopenerp: BRAND || null });
    },
});

/* ------------------------------------------------------------------
 * 2. Menu utilisateur : Documentation / Support / Mon compte Odoo
 * ------------------------------------------------------------------ */
const userMenu = registry.category("user_menuitems");

function retargetMenuItem(key, url, label, sequence) {
    if (!userMenu.contains(key)) {
        return;
    }
    userMenu.remove(key);
    if (!url) {
        return;
    }
    userMenu.add(
        key,
        () => ({
            type: "item",
            id: key,
            description: label,
            href: url,
            callback: () => window.open(url, "_blank", "noopener"),
            sequence: sequence,
        }),
        { force: true }
    );
}

retargetMenuItem("documentation", branding.documentation_url, _t("Documentation"), 10);
retargetMenuItem("support", branding.support_url, _t("Support"), 20);
retargetMenuItem("odoo_account", "", "", 30);

/* ------------------------------------------------------------------
 * 3. Titres des boîtes de dialogue d'erreur
 * ------------------------------------------------------------------ */
if (BRAND) {
    const titles = {
        ErrorDialog: _t("Error"),
        ClientErrorDialog: _t("Client Error"),
        NetworkErrorDialog: _t("Network Error"),
        RPCErrorDialog: _t("Server Error"),
        Error504Dialog: _t("Request timeout"),
    };
    for (const [name, suffix] of Object.entries(titles)) {
        const DialogClass = errorDialogs[name];
        if (DialogClass) {
            try {
                DialogClass.title = `${BRAND} - ${suffix}`;
            } catch {
                // classe scellée : on ignore.
            }
        }
    }
}
