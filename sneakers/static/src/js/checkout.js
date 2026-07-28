(function () {

    var checkoutSection = document.querySelector(".sn-checkout");
    if (!checkoutSection) return;

    var progressSteps = document.querySelectorAll(".sn-progress-step");
    var TOTAL_STEPS   = progressSteps.length || 4;
    var currentStep   = 1;

    setupStepNavigation();
    updateProgressBar(currentStep);
    updateShippingTotal();

    function updateProgressBar(step) {
        progressSteps.forEach(function (el, i) {
            var num = i + 1;
            el.classList.remove("active", "completed");

            if (num < step)  el.classList.add("completed");
            if (num === step) el.classList.add("active");

            var progressLine = document.querySelector(".sn-progress-line");
            if (progressLine && TOTAL_STEPS > 1) {
                var pct = ((step - 1) / (TOTAL_STEPS - 1)) * 100;
                progressLine.style.width = "calc(" + pct + "% * (1 - 55px / 100%) + " + (pct / 100 * 27.5) + "px)";
            }
        });
    }

    function setupStepNavigation() {
        var checkoutCards = checkoutSection.querySelectorAll(".sn-checkout-card");
        // Bouton retour + clic sur cercle de progression pour toutes les cartes
        checkoutCards.forEach(function (card, i) {
            var stepNum = i + 1;
            card.dataset.step = stepNum;
            card.style.display = (stepNum === currentStep) ? "block" : "none";
            if (stepNum > 1 && !card.querySelector(".sn-step-prev-btn")) {
                var prevBtn       = document.createElement("button");
                prevBtn.className = "sn-step-prev-btn";
                prevBtn.type      = "button";
                prevBtn.textContent = "← Retour";
                card.insertBefore(prevBtn, card.firstChild);
                prevBtn.addEventListener("click", function () { goToStep(stepNum - 1); });
            }
            if (progressSteps[i]) {
                progressSteps[i].addEventListener("click", function () {
                    if (stepNum < currentStep) goToStep(stepNum);
                });
                progressSteps[i].style.cursor = "pointer";
            }
        });
        // Carte 1 — Billing Address : "Continuer"
        var card1 = checkoutCards[0];
        if (card1 && !card1.querySelector(".sn-step-next-btn")) {
            var btn1        = document.createElement("button");
            btn1.className  = "sn-btn-primary sn-step-next-btn";
            btn1.type       = "button";
            btn1.textContent = "Continue";
            card1.appendChild(btn1);
            btn1.addEventListener("click", function () {
                if (validateStep(card1, 1)) goToStep(2);
            });
        }
        // Carte 2 — Shipping Method : "Continuer"
        var card2 = checkoutCards[1];
        if (card2 && !card2.querySelector(".sn-step-next-btn")) {
            var btn2        = document.createElement("button");
            btn2.className  = "sn-btn-primary sn-step-next-btn";
            btn2.type       = "button";
            btn2.textContent = "Continue";
            card2.appendChild(btn2);
            btn2.addEventListener("click", function () {
                if (validateStep(card2, 2)) goToStep(3);
            });
        }
        // Carte 3 — Payment Method : bouton dynamique selon choix
        var card3 = checkoutCards[2];
        if (card3) setupPaymentMethodCard(card3, checkoutCards[3]);
        // Carte 4 — Payment Details : "Confirm my order"
        var card4 = checkoutCards[3];
        if (card4) setupPaymentDetailsCard(card4);
    }

    function setupPaymentMethodCard(card, card4) {
        var actionWrap       = document.createElement("div");
        actionWrap.className = "sn-payment-action-wrap";
        card.appendChild(actionWrap);
        function refreshButton() {
            var selected = card.querySelector("input[name='payment']:checked");
            actionWrap.innerHTML = "";
            if (!selected) return;
            var btn       = document.createElement("button");
            btn.type      = "button";
            btn.className = "sn-btn-primary sn-step-next-btn";
            if (selected.value === "cash") {
                btn.textContent = "Confirm my order";
                btn.addEventListener("click", function () { submitOrder(btn); });
            } else {
                btn.textContent = "Proceed to payment";
                btn.addEventListener("click", function () {
                    // Affiche la bonne section dans la carte 4
                    if (card4) {
                        card4.querySelectorAll(".sn-payment-section").forEach(function (s) {
                            s.style.display = "none";
                        });
                        var target = card4.querySelector(".sn-payment-section--" + selected.value);
                        if (target) target.style.display = "block";
                    }
                    goToStep(4);
                });
            }
            actionWrap.appendChild(btn);
        }
        card.querySelectorAll("input[name='payment']").forEach(function (radio) {
            radio.addEventListener("change", refreshButton);
        });
    }

    function setupPaymentDetailsCard(card) {
        var confirmBtn        = document.createElement("button");
        confirmBtn.className  = "sn-btn-primary sn-confirm-order-btn";
        confirmBtn.type       = "button";
        confirmBtn.textContent = "Confirm my order";
        card.appendChild(confirmBtn);
        confirmBtn.addEventListener("click", function () { submitOrder(confirmBtn); });
    }



    function goToStep(step) {
        step = Math.max(1, Math.min(TOTAL_STEPS, step));
        currentStep = step;

        var checkoutCards = checkoutSection.querySelectorAll(".sn-checkout-card");
        checkoutCards.forEach(function (card, i) {
            card.style.display = (i + 1 === step) ? "block" : "none";
        });

        updateProgressBar(step);

        checkoutSection.scrollIntoView({ behavior: "smooth", block: "start" });
    }

    function createConfirmButton() {
        var btn = document.createElement("button");
        btn.className   = "sn-checkout-btn sn-confirm-order-btn";
        btn.type        = "button";
        btn.textContent = "Confirm my order";
        var lastCard    = checkoutSection.querySelectorAll(".sn-checkout-card");
        var last        = lastCard[lastCard.length - 1];
        if (last) last.appendChild(btn);
        return btn;
    }

    function validateStep(card, stepNum) {
        var valid = true;

        card.querySelectorAll(".sn-field-error").forEach(function (el) { el.remove(); });
        card.querySelectorAll(".sn-form-group--error").forEach(function (el) {
            el.classList.remove("sn-form-group--error");
        });

        var requiredFields = card.querySelectorAll("input[required], select[required], input:not([type='radio']):not([type='checkbox'])");

        requiredFields.forEach(function (field) {
            if (!field.value.trim()) {
                valid = false;
                markFieldError(field, "Ce champ est obligatoire");
            }
        });

        // Validation email
        var emailField = card.querySelector("input[type='email']");
        if (emailField && emailField.value.trim()) {
            if (!/^[^\s@]+@[^\s@]+\.[^\s@]+$/.test(emailField.value)) {
                valid = false;
                markFieldError(emailField, "Adresse email invalide");
            }
        }

        // Validation téléphone
        var telField = card.querySelector("input[type='tel']");
        if (telField && telField.value.trim()) {
            if (!/^[\d\s\+\-\(\)]{7,20}$/.test(telField.value)) {
                valid = false;
                markFieldError(telField, "Numéro de téléphone invalide");
            }
        }

        // Étape paiement : au moins un mode sélectionné
        if (stepNum === TOTAL_STEPS) {
            var paymentRadios = card.querySelectorAll("input[name='payment']");
            var paymentOk     = false;
            paymentRadios.forEach(function (r) { if (r.checked) paymentOk = true; });

            if (paymentRadios.length > 0 && !paymentOk) {
                valid = false;
                if (window.snShowToast) {
                    window.snShowToast("Veuillez sélectionner un mode de paiement.", "error");
                }
            }
        }

        if (!valid) {
            var firstError = card.querySelector(".sn-form-group--error input, .sn-form-group--error select");
            if (firstError) firstError.focus();
        }

        return valid;
    }

    function markFieldError(field, message) {
        var group = field.closest(".sn-form-group") || field.parentElement;
        if (group) group.classList.add("sn-form-group--error");

        var errMsg = document.createElement("span");
        errMsg.className   = "sn-field-error";
        errMsg.textContent = message;

        var afterEl = field.nextSibling;
        field.parentNode.insertBefore(errMsg, afterEl);

        field.addEventListener("input", function clearErr() {
            errMsg.remove();
            if (group) group.classList.remove("sn-form-group--error");
            field.removeEventListener("input", clearErr);
        });
    }

    function updateShippingTotal() {
        var shippingRadios = document.querySelectorAll("input[name='shipping']");

        shippingRadios.forEach(function (radio) {
            radio.addEventListener("change", function () {
                var card    = this.closest(".sn-radio-card");
                var priceEl = card ? card.querySelector("span:last-child") : null;
                var price   = priceEl ? priceEl.textContent.trim() : "Free";

                var shippingLine = document.querySelector(".sn-order-shipping, .sn-summary-shipping");
                if (shippingLine) shippingLine.textContent = price;

                // Recalcule le total
                recalculateOrderTotal();
            });
        });
    }

    function recalculateOrderTotal() {
        var subtotalEl  = document.querySelector(".sn-order-subtotal, .sn-summary-subtotal");
        var shippingEl  = document.querySelector(".sn-order-shipping, .sn-summary-shipping");
        var totalEl     = document.querySelector(".sn-order-total, .sn-summary-total");

        if (!subtotalEl || !totalEl) return;

        var subtotal = parseFloat((subtotalEl.textContent || "0").replace(/[^0-9.]/g, "")) || 0;
        var shipping = shippingEl && shippingEl.textContent.toLowerCase() !== "free"
                       ? parseFloat((shippingEl.textContent || "0").replace(/[^0-9.]/g, "")) || 0
                       : 0;

        totalEl.textContent = "$" + (subtotal + shipping).toFixed(2);
    }

    // AUTOCOMPLÉTION VILLES
    var cityInput = document.querySelector(".sn-checkout input[placeholder='Casablanca'], .sn-checkout .sn-city-input");

    if (cityInput) {
        var DEMO_CITIES = [
            "Casablanca", "Rabat", "Marrakech", "Fès", "Tanger", "Agadir",
            "Meknès", "Oujda", "Salé", "Tétouan", "Paris", "Lyon", "Marseille",
            "Madrid", "Barcelona", "Dubai", "Montreal", "Brussels"
        ];

        var cityDropdown = document.createElement("ul");
        cityDropdown.className = "sn-city-autocomplete";
        cityDropdown.style.display = "none";
        cityInput.parentNode.style.position = "relative";
        cityInput.parentNode.appendChild(cityDropdown);

        cityInput.addEventListener("input", function () {
            var val = this.value.trim();
            cityDropdown.innerHTML = "";

            if (val.length < 2) { cityDropdown.style.display = "none"; return; }

            /* backend */

            var matches = DEMO_CITIES.filter(function (city) {
                return city.toLowerCase().indexOf(val.toLowerCase()) === 0;
            });

            if (!matches.length) { cityDropdown.style.display = "none"; return; }

            matches.forEach(function (city) {
                var li = document.createElement("li");
                li.textContent = city;
                li.addEventListener("click", function () {
                    cityInput.value          = city;
                    cityDropdown.style.display = "none";
                });
                cityDropdown.appendChild(li);
            });

            cityDropdown.style.display = "block";
        });

        document.addEventListener("click", function (e) {
            if (!cityInput.parentNode.contains(e.target)) {
                cityDropdown.style.display = "none";
            }
        });
    }

    function submitOrder(btn) {
        btn.disabled    = true;
        btn.textContent = "Processing in progress...";

        /* backend */
        
        setTimeout(function () {
            window.location.href = "/confirmation?order=CMD-2026-" +
                Math.floor(10000 + Math.random() * 89999);
        }, 1200);
    }

})();
