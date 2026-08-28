/** @odoo-module **/

document.addEventListener("change", (event) => {
    if (!event.target.closest(".cs-custom_filters")) {
        return;
    }

    const params = new URLSearchParams(window.location.search);

    // Vegan
    const vegan = document.querySelector("#filter_vegan");

    if (vegan?.checked) {
        params.set("vegan", "1");
    } else {
        params.delete("vegan");
    }

    // Allergènes
    params.delete("allergens_exclude");

    document
        .querySelectorAll(
            ".cs-custom_filters input[name='allergens_exclude']:checked"
        )
        .forEach((input) => {
            params.append("allergens_exclude", input.value);
        });

    // Retour à la page boutique avec les nouveaux filtres
    window.location.href = `${window.location.pathname}?${params.toString()}`;
});