import { Interaction } from "@web/public/interaction";
import { registry } from "@web/core/registry";

/**
 * Ajoute, sur le formulaire de paiement du checkout, un drapeau français
 * puis un badge « Entités publiques » à la suite du libellé de l'option
 * « Mandat administratif ».
 */
export class MandatAdministratifPaymentBadge extends Interaction {
    static selector = "form[name='o_payment_form']";

    start() {
        const input = this.el.querySelector(
            "input[data-provider-code='mandat_administratif']," +
            " input[data-payment-method-code='mandat_administratif']"
        );
        if (!input) {
            return;
        }
        const label = input.closest("label") || input.parentElement;
        if (!label || label.querySelector(".o_ma_flag")) {
            return;
        }

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
        badge.className = "o_ma_checkout_badge badge rounded-pill text-bg-primary ms-auto";
        badge.textContent = "Entités publiques";

        label.classList.add("o_ma_option_label");
        this.insert(flag, label, "beforeend");
        this.insert(badge, label, "beforeend");
    }
}

registry
    .category("public.interactions")
    .add("mandat_administratif.payment_badge", MandatAdministratifPaymentBadge);
