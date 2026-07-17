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
        if (!label || label.querySelector(".o_ma_checkout_badge")) return;

        const badge = document.createElement("span");
        badge.className =
            "o_ma_checkout_badge badge rounded-pill text-bg-primary ms-auto";
        badge.textContent = "Entités publiques";

        label.classList.add("o_ma_option_label");
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
