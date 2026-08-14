/** @odoo-module **/

import { Interaction } from "@web/public/interaction";
import { registry } from "@web/core/registry";
import { _t } from "@web/core/l10n/translation";

/**
 * Confirmation avant retrait d'un consentement déjà accordé.
 *
 * Le retrait est un droit (art. 7.3) : on ne le bloque jamais, on se contente
 * d'expliquer la conséquence pour éviter les décochages accidentels.
 */
export class RgpdConsentForm extends Interaction {
    static selector = ".o_rgpd_consent_form";

    dynamicContent = {
        "_root:t-on-submit": this.onSubmit,
    };

    setup() {
        this.initialState = new Map();
        for (const input of this.el.querySelectorAll("input[type='checkbox']")) {
            this.initialState.set(input.name, input.checked);
        }
    }

    onSubmit(ev) {
        const withdrawn = [];
        for (const input of this.el.querySelectorAll("input[type='checkbox']")) {
            if (this.initialState.get(input.name) && !input.checked) {
                const label = this.el.querySelector(`label[for="${input.id}"]`);
                withdrawn.push(label ? label.textContent.trim() : input.name);
            }
        }
        if (!withdrawn.length) {
            return;
        }
        const message = _t(
            "Vous retirez votre consentement pour : %s.\n\n" +
            "Le retrait prend effet immédiatement, sans remettre en cause la " +
            "licéité des traitements déjà réalisés. Confirmer ?",
            withdrawn.join(", ")
        );
        if (!window.confirm(message)) {
            ev.preventDefault();
            ev.stopPropagation();
        }
    }
}

/**
 * Avertissement lorsque la personne sélectionne une demande d'effacement :
 * l'opération est irréversible et peut résilier des services en cours.
 */
export class RgpdRequestForm extends Interaction {
    static selector = "form[action='/my/privacy/request'], form[action='/rgpd/demande/envoi']";

    dynamicContent = {
        "select[name='request_type']:t-on-change": this.onTypeChange,
        "textarea[name='description']:t-on-input": this.onDescriptionInput,
    };

    setup() {
        this.noticeEl = null;
        this.counterEl = null;
        this.maxLength = 5000;
    }

    start() {
        const textarea = this.el.querySelector("textarea[name='description']");
        if (textarea) {
            textarea.setAttribute("maxlength", String(this.maxLength));
            this.counterEl = document.createElement("div");
            this.counterEl.className = "o_rgpd_counter text-muted mt-1";
            textarea.insertAdjacentElement("afterend", this.counterEl);
            this.registerCleanup(() => this.counterEl.remove());
            this.updateCounter(textarea.value.length);
        }
    }

    updateCounter(length) {
        if (!this.counterEl) {
            return;
        }
        const remaining = this.maxLength - length;
        this.counterEl.textContent = _t("%s caractères restants", remaining);
        this.counterEl.classList.toggle("text-danger", remaining < 200);
    }

    onDescriptionInput(ev) {
        this.updateCounter(ev.target.value.length);
    }

    onTypeChange(ev) {
        const value = ev.target.value;
        if (this.noticeEl) {
            this.noticeEl.remove();
            this.noticeEl = null;
        }
        let text = null;
        if (value === "erasure") {
            text = _t(
                "L'effacement est irréversible. Certaines données devront être " +
                "conservées si la loi nous l'impose (facturation, comptabilité, " +
                "garanties). Les services en cours peuvent être interrompus."
            );
        } else if (value === "withdraw") {
            text = _t(
                "Le retrait du consentement prend effet pour l'avenir et " +
                "n'affecte pas la licéité des traitements déjà réalisés."
            );
        } else if (value === "objection") {
            text = _t(
                "Précisez les raisons tenant à votre situation particulière : " +
                "elles sont nécessaires à l'examen de votre opposition, sauf en " +
                "matière de prospection commerciale."
            );
        }
        if (!text) {
            return;
        }
        this.noticeEl = document.createElement("div");
        this.noticeEl.className = "alert alert-warning mt-2 small";
        this.noticeEl.setAttribute("role", "alert");
        this.noticeEl.textContent = text;
        ev.target.insertAdjacentElement("afterend", this.noticeEl);
        this.registerCleanup(() => {
            if (this.noticeEl) {
                this.noticeEl.remove();
                this.noticeEl = null;
            }
        });
    }
}

registry
    .category("public.interactions")
    .add("exocoms_rgpd.consent_form", RgpdConsentForm);

registry
    .category("public.interactions")
    .add("exocoms_rgpd.request_form", RgpdRequestForm);
