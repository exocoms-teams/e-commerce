/** @odoo-module **/

import publicWidget from "@web/legacy/js/public/public_widget";

publicWidget.registry.AutoCompareButtons = publicWidget.Widget.extend({
    selector: "[data-auto-compare-link]",
    start() {
        this.el.addEventListener("click", (ev) => {
            const label = this.el.dataset.autoCompareLabel || "vehicle";
            this.el.textContent = `Added ${label}`;
        });
        return this._super(...arguments);
    },
});
