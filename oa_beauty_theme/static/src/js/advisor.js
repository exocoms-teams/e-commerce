/** @odoo-module **/

import { _t } from "@web/core/l10n/translation";

function escapeHtml(value) {
    return String(value || "").replace(/[&<>"']/g, (char) => ({
        "&": "&amp;",
        "<": "&lt;",
        ">": "&gt;",
        '"': "&quot;",
        "'": "&#039;",
    })[char]);
}

function jsonRpc(url, params) {
    return fetch(url, {
        method: "POST",
        headers: { "Content-Type": "application/json" },
        body: JSON.stringify({ jsonrpc: "2.0", method: "call", params: params || {} }),
    }).then((response) => response.json()).then((payload) => {
        if (payload.error) {
            throw new Error(payload.error.data?.message || payload.error.message || "RPC error");
        }
        return payload.result || {};
    });
}

const OaAdvisor = {
    currentStep: 1,
    totalSteps: 5,
    profile: {},

    init() {
        this.bindEvents();
        this.showStep(1);
    },

    bindEvents() {
        document.querySelectorAll(".oa-advisor-option").forEach((btn) => {
            btn.addEventListener("click", (e) => this.selectOption(e.currentTarget));
        });
        document.getElementById("oa_advisor_next")?.addEventListener("click", () => this.nextStep());
        document.getElementById("oa_advisor_back")?.addEventListener("click", () => this.prevStep());
        document.getElementById("oa_advisor_restart")?.addEventListener("click", () => this.restart());
    },

    selectOption(btn) {
        const container = btn.closest(".oa-advisor-options");
        container.querySelectorAll(".oa-advisor-option").forEach((b) => b.classList.remove("selected"));
        btn.classList.add("selected");
        this.profile[container.dataset.field] = btn.dataset.value;
        const nextBtn = document.getElementById("oa_advisor_next");
        if (nextBtn) {
            nextBtn.disabled = false;
        }
    },

    updateProgress() {
        const pct = (this.currentStep / this.totalSteps) * 100;
        const bar = document.getElementById("oa_advisor_progress");
        const label = document.getElementById("oa_advisor_step_label");
        if (bar) {
            bar.style.width = pct + "%";
        }
        if (label) {
            label.textContent = _t("Étape %s sur %s", this.currentStep, this.totalSteps);
        }
    },

    showStep(step) {
        document.querySelectorAll(".oa-advisor-step").forEach((el) => el.classList.remove("active"));
        const target = document.querySelector(`.oa-advisor-step[data-step="${step}"]`);
        if (target) {
            target.classList.add("active");
        }

        const nextBtn = document.getElementById("oa_advisor_next");
        const backBtn = document.getElementById("oa_advisor_back");
        if (nextBtn) {
            const field = target?.querySelector(".oa-advisor-options")?.dataset.field;
            nextBtn.disabled = Boolean(field && !this.profile[field]);
            nextBtn.textContent = step === this.totalSteps ? _t("Obtenir ma routine") : _t("Suivant →");
        }
        if (backBtn) {
            backBtn.style.display = step > 1 ? "inline-block" : "none";
        }
        this.updateProgress();
    },

    nextStep() {
        if (this.currentStep < this.totalSteps) {
            this.currentStep += 1;
            this.showStep(this.currentStep);
        } else {
            this.submitQuiz();
        }
    },

    prevStep() {
        if (this.currentStep > 1) {
            this.currentStep -= 1;
            this.showStep(this.currentStep);
        }
    },

    async submitQuiz() {
        const quizEl = document.getElementById("oa_advisor_quiz");
        const loadingEl = document.getElementById("oa_advisor_loading");
        if (quizEl) {
            quizEl.style.display = "none";
        }
        if (loadingEl) {
            loadingEl.style.display = "block";
            loadingEl.innerHTML = `<div class="oa-advisor-spinner"></div><p>${escapeHtml(_t("Nous préparons votre routine personnalisée…"))}</p>`;
        }

        try {
            const result = await jsonRpc("/api/advisor/recommend", this.profile);
            if (loadingEl) {
                loadingEl.style.display = "none";
            }
            this.renderResults(result);
        } catch (e) {
            if (loadingEl) {
                loadingEl.innerHTML = `<p class="text-danger">${escapeHtml(_t("Une erreur est survenue. Veuillez réessayer."))}</p>`;
            }
            console.error("[OA Advisor]", e);
        }
    },

    renderResults(result) {
        const resultsEl = document.getElementById("oa_advisor_results");
        if (!resultsEl) {
            return;
        }

        const explanation = result?.explanation || _t("Aucune recommandation n'est disponible pour le moment.");
        const expEl = document.getElementById("oa_advisor_explanation");
        if (expEl) {
            expEl.innerHTML = `<p class="oa-advisor-explain-text"><i class="fa fa-leaf me-2"></i>${escapeHtml(explanation)}</p>`;
        }

        const routineEl = document.getElementById("oa_advisor_routine");
        const routine = result?.routine || [];
        if (routineEl) {
            if (!routine.length) {
                routineEl.innerHTML = `<p>${escapeHtml(_t("Aucun produit publié ne correspond actuellement à ce profil."))}</p>`;
            } else {
                routineEl.innerHTML = routine.map((step, index) => `
                    <div class="oa-advisor-routine-step">
                        <div class="oa-advisor-step-number">${index + 1}</div>
                        <div class="oa-advisor-step-info">
                            <strong>${escapeHtml(step.step || "")}</strong>
                            <span>${escapeHtml(step.product || "")}</span>
                            <p>${escapeHtml(step.desc || "")}</p>
                        </div>
                    </div>
                `).join("");
            }
        }

        const productsEl = document.getElementById("oa_advisor_products");
        const products = result?.products || [];
        if (productsEl) {
            if (!products.length) {
                productsEl.innerHTML = `<p>${escapeHtml(_t("Aucun produit trouvé"))}</p>`;
            } else {
                productsEl.innerHTML = products.map((product) => {
                    const reasons = (product.match_reasons || []).map((reason) => `<li>${escapeHtml(reason)}</li>`).join("");
                    const price = product.price_formatted || product.price;
                    return `
                        <a href="${escapeHtml(product.url || "/shop")}" class="oa-advisor-product-card">
                            <div class="oa-advisor-product-img-wrap">
                                <img src="${escapeHtml(product.image_url || "")}" alt="${escapeHtml(product.name || "")}" loading="lazy"/>
                            </div>
                            <div class="oa-advisor-product-info">
                                <div class="oa-advisor-product-name">${escapeHtml(product.name || "")}</div>
                                <div class="oa-advisor-product-price">${price}</div>
                                ${reasons ? `<ul class="oa-advisor-product-reasons">${reasons}</ul>` : ""}
                                <div class="oa-advisor-product-cta">${escapeHtml(_t("Voir le produit"))}</div>
                            </div>
                        </a>
                    `;
                }).join("");
            }
        }

        resultsEl.style.display = "block";
        resultsEl.scrollIntoView({ behavior: "smooth", block: "start" });
    },

    restart() {
        this.currentStep = 1;
        this.profile = {};
        document.querySelectorAll(".oa-advisor-option").forEach((b) => b.classList.remove("selected"));
        const resultsEl = document.getElementById("oa_advisor_results");
        const quizEl = document.getElementById("oa_advisor_quiz");
        const loadingEl = document.getElementById("oa_advisor_loading");
        if (resultsEl) {
            resultsEl.style.display = "none";
        }
        if (loadingEl) {
            loadingEl.style.display = "none";
        }
        if (quizEl) {
            quizEl.style.display = "block";
        }
        this.showStep(1);
    },
};

function initOaAdvisor() {
    if (document.getElementById("oa_advisor_quiz") && !window.oaAdvisorInitialized) {
        window.oaAdvisorInitialized = true;
        OaAdvisor.init();
    }
}

if (document.readyState === "loading") {
    document.addEventListener("DOMContentLoaded", initOaAdvisor);
} else {
    initOaAdvisor();
}
