document.addEventListener(
    "change",
    (event) => {
        const checkbox = event.target.closest(".js_allergen_filter");

        if (!checkbox) {
            return;
        }

        const form = checkbox.closest("form");

        if (!form) {
            return;
        }

        // Prevent Odoo's shop filter handler from processing this change.
        event.preventDefault();
        event.stopImmediatePropagation();

        const params = new URLSearchParams();

        // Preserve all the normal shop filter parameters.
        for (const [key, value] of new FormData(form).entries()) {
            params.append(key, value);
        }

        // FormData already contains all checked allergen checkboxes.
        window.location.href = `${form.action}?${params.toString()}`;
    },
    true, // capture phase: run before Odoo's change handler
);