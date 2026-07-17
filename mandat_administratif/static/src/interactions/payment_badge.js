/**
 * Ajoute un drapeau français et un badge « Entités publiques »
 * à côté du libellé « Mandat administratif » au checkout.
 * Utilise vanilla JS pour éviter les dépendances OWL/Interaction.
 */
(function () {
    function addMandatBadge() {
        const selectors = [
            "input[data-provider-code='mandat_administratif']",
            "input[data-payment-method-code='mandat_administratif']",
        ];

        let input = null;
        for (const sel of selectors) {
            input = document.querySelector(sel);
            if (input) break;
        }
        if (!input) return;

        const label = input.closest("label") || input.parentElement;
        if (!label || label.querySelector(".o_ma_flag")) return;

        const flag = document.createElement("span");
        flag.className = "o_ma_flag ms-2";
        flag.setAttribute("role", "img");
        flag.setAttribute("aria-label", "France");
        flag.innerHTML =
            '<svg width="28" height="19" viewBox="0 0 21 14"' +
            ' xmlns="http://www.w3.org/2000/svg">' +
            '<rect width="7" height="14" fill="#0055A4"/>' +
            '<rect x="7" width="7" height="14" fill="#FFFFFF"/>' +
            '<rect x="14" width="7" height="14" fill="#EF4135"/>' +
            "</svg>";

        const badge = document.createElement("span");
        badge.className =
            "o_ma_checkout_badge badge rounded-pill text-bg-primary ms-auto";
        badge.textContent = "Entités publiques";

        label.classList.add("o_ma_option_label");
        label.appendChild(flag);
        label.appendChild(badge);
    }

    if (document.readyState === "loading") {
        document.addEventListener("DOMContentLoaded", addMandatBadge);
    } else {
        addMandatBadge();
    }
    // Fallback pour les formulaires chargés dynamiquement
    setTimeout(addMandatBadge, 800);
})();
