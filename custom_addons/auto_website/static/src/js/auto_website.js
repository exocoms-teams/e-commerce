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
        this._setupPriceRange();
        return this._super(...arguments);
    },

    _setupPriceRange() {
        const range = this.el.querySelector(".auto-price-range");
        if (!range) {
            return;
        }
        const minInput = range.querySelector(".auto-range-min");
        const maxInput = range.querySelector(".auto-range-max");
        const minLabel = range.querySelector("[data-auto-price-min-label]");
        const maxLabel = range.querySelector("[data-auto-price-max-label]");
        const fill = range.querySelector("[data-auto-price-range-fill]");
        if (!minInput || !maxInput || !minLabel || !maxLabel || !fill) {
            return;
        }

        const minBound = Number(range.dataset.min || minInput.min || 0);
        const maxBound = Number(range.dataset.max || maxInput.max || 0);
        const formatter = new Intl.NumberFormat("fr-FR", {
            style: "currency",
            currency: "EUR",
            maximumFractionDigits: 0,
        });

        const syncRange = (changedInput) => {
            let minValue = Number(minInput.value || minBound);
            let maxValue = Number(maxInput.value || maxBound);
            if (minValue > maxValue) {
                if (changedInput === minInput) {
                    maxValue = minValue;
                    maxInput.value = String(maxValue);
                } else {
                    minValue = maxValue;
                    minInput.value = String(minValue);
                }
            }
            minLabel.textContent = formatter.format(minValue);
            maxLabel.textContent = formatter.format(maxValue);

            const span = Math.max(maxBound - minBound, 1);
            const left = ((minValue - minBound) / span) * 100;
            const right = 100 - ((maxValue - minBound) / span) * 100;
            fill.style.left = `${Math.max(0, Math.min(left, 100))}%`;
            fill.style.right = `${Math.max(0, Math.min(right, 100))}%`;
        };

        minInput.addEventListener("input", () => syncRange(minInput));
        maxInput.addEventListener("input", () => syncRange(maxInput));
        syncRange();
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
