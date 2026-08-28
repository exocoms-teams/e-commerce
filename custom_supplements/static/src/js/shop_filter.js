import publicWidget from "@web/legacy/js/public/public_widget";

publicWidget.registry.CustomSupplementFilters = publicWidget.Widget.extend({
    selector: ".cs-custom_filters",

    events: {
        "change input": "_onFilterChange",
    },

    _onFilterChange: function () {
        console.log("shop filter loaded")
        const params = new URLSearchParams(window.location.search);

        const vegan = this.el.querySelector("#filter_vegan");

        if (vegan?.checked) {
            params.set("vegan", "1");
        } else {
            params.delete("vegan");
        }

        params.delete("allergens_exclude");

        this.el
            .querySelectorAll("input[name='allergens_exclude']:checked")
            .forEach((input) => {
                params.append("allergens_exclude", input.value);
            });

        window.location.search = params.toString();
    },
});