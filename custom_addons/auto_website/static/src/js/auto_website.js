/** @odoo-module **/

import publicWidget from "@web/legacy/js/public/public_widget";

publicWidget.registry.AutoCatalogUX = publicWidget.Widget.extend({
    selector: ".auto-filter-bar",
    start() {
        const selects = this.el.querySelectorAll("select");
        for (const select of selects) {
            select.addEventListener("change", () => {
                if (select.name === "sort") {
                    this.el.submit();
                }
            });
        }
        return this._super(...arguments);
    },
});

publicWidget.registry.AutoBrandScroller = publicWidget.Widget.extend({
    selector: ".auto-brand-scroll",
    start() {
        this.el.addEventListener("wheel", (event) => {
            if (Math.abs(event.deltaY) <= Math.abs(event.deltaX)) {
                return;
            }
            event.preventDefault();
            this.el.scrollLeft += event.deltaY;
        }, { passive: false });
        return this._super(...arguments);
    },
});
