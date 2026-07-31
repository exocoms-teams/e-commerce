(function () {

    var checkoutSection = document.querySelector(".sn-checkout");
    if (!checkoutSection) return;

    // ponytail: stripped multi-step wizard — all checkout cards visible at once
    // kept: validation, city autocomplete, shipping recalc

    var checkoutCards = checkoutSection.querySelectorAll(".sn-checkout-card");

    // Show all cards
    checkoutCards.forEach(function (card) {
        card.style.display = "block";
    });

    // Confirm & Pay button — validate all then submit
    var confirmBtns = document.querySelectorAll(".sn-confirm-btn, .sn-place-order-btn");
    confirmBtns.forEach(function (btn) {
        btn.addEventListener("click", function (e) {
            var allValid = true;
            checkoutCards.forEach(function (card) {
                if (card.style.display === "none") return;
                if (!validateCard(card)) allValid = false;
            });
            if (!allValid) {
                e.preventDefault();
            }
        });
    });

    function validateCard(card) {
        var valid = true;

        card.querySelectorAll(".sn-field-error").forEach(function (el) { el.remove(); });
        card.querySelectorAll(".sn-form-group--error").forEach(function (el) {
            el.classList.remove("sn-form-group--error");
        });

        var requiredFields = card.querySelectorAll("input[required], select[required]");

        requiredFields.forEach(function (field) {
            if (!field.value.trim()) {
                valid = false;
                markFieldError(field, "This field is required");
            }
        });

        var emailField = card.querySelector("input[type='email']");
        if (emailField && emailField.value.trim()) {
            if (!/^[^\s@]+@[^\s@]+\.[^\s@]+$/.test(emailField.value)) {
                valid = false;
                markFieldError(emailField, "Invalid email address");
            }
        }

        var telField = card.querySelector("input[type='tel']");
        if (telField && telField.value.trim()) {
            if (!/^[\d\s\+\-\(\)]{7,20}$/.test(telField.value)) {
                valid = false;
                markFieldError(telField, "Invalid phone number");
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

    // City autocomplete
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

            var matches = DEMO_CITIES.filter(function (city) {
                return city.toLowerCase().indexOf(val.toLowerCase()) === 0;
            });

            if (!matches.length) { cityDropdown.style.display = "none"; return; }

            matches.forEach(function (city) {
                var li = document.createElement("li");
                li.textContent = city;
                li.addEventListener("click", function () {
                    cityInput.value = city;
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

})();
