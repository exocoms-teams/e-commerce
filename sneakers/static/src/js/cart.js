(function () {

    var cartSection = document.querySelector(".sn-cart");
    if (!cartSection) return;

    // BOUTONS +/- QUANTITÉ
    cartSection.addEventListener("click", function (e) {

        var btn = e.target.closest(".sn-qty-btn");
        if (!btn) return;

        var cartItem = btn.closest(".sn-cart-item");
        if (!cartItem) return;

        var input  = cartItem.querySelector("input[type='number']");
        if (!input) return;

        var current = parseInt(input.value, 10) || 1;
        var text    = btn.textContent.trim();

        if (text === "+" || btn.dataset.action === "increase") {
            input.value = current + 1;
        } else if (text === "-" || btn.dataset.action === "decrease") {
            if (current > 1) input.value = current - 1;
        }

        updateItemTotal(cartItem, input.value);
        syncWithBackend(cartItem, input.value);
    });

    // Saisie directe dans l'input
    cartSection.addEventListener("change", function (e) {
        if (e.target.type !== "number") return;

        var cartItem = e.target.closest(".sn-cart-item");
        if (!cartItem) return;

        var val = parseInt(e.target.value, 10);
        if (isNaN(val) || val < 1) { e.target.value = 1; val = 1; }

        updateItemTotal(cartItem, val);
        syncWithBackend(cartItem, val);
    });

    // SUPPRESSION D'UN ARTICLE
    cartSection.addEventListener("click", function (e) {

        var removeBtn = e.target.closest(".sn-cart-remove");
        if (!removeBtn) return;

        var cartItem = removeBtn.closest(".sn-cart-item");
        if (!cartItem) return;

        var lineId = cartItem.dataset.lineId;

        removeLineBackend(lineId).then(function (data) {
            // Animation de sortie
            cartItem.style.transition = "opacity 0.3s, transform 0.3s";
            cartItem.style.opacity    = "0";
            cartItem.style.transform  = "translateX(40px)";

            setTimeout(function () {
                cartItem.remove();
                applyCartTotals(data);
                checkEmptyCart();
            }, 300);
        });
    });

    // CALCUL TOTAL PAR ARTICLE (estimation optimiste en attendant la réponse serveur)
    function updateItemTotal(cartItem, qty) {
        var priceEl = cartItem.querySelector(".sn-cart-price");
        var totalEl = cartItem.querySelector(".sn-cart-total");
        if (!priceEl || !totalEl) return;

        var price = parsePrice(priceEl.textContent);
        var total = price * parseInt(qty, 10);

        totalEl.textContent = formatPrice(total);
    }

    // MISE À JOUR DES TOTAUX GÉNÉRAUX À PARTIR DE LA RÉPONSE SERVEUR (source de vérité)
    function applyCartTotals(data) {
        if (!data) return;

        setHtmlIfExists(".sn-order-subtotal", data.subtotal_html);
        setHtmlIfExists(".sn-order-tax",      data.tax_html);
        setHtmlIfExists(".sn-order-total",    data.total_html);

        updateCartBadge(data.cart_quantity);
    }

    // CODE PROMO
    var promoForm = document.querySelector(".sn-promo-form");
    if (promoForm) {
        promoForm.addEventListener("submit", function (e) {
            e.preventDefault();
            applyPromoCode();
        });

        var promoBtn = promoForm.querySelector("button");
        if (promoBtn) {
            promoBtn.addEventListener("click", function (e) {
                e.preventDefault();
                applyPromoCode();
            });
        }
    }

    function applyPromoCode() {
        var input = document.querySelector(".sn-promo-form input");
        if (!input) return;

        var code = input.value.trim().toUpperCase();
        if (!code) return;

        var msgEl = document.querySelector(".sn-promo-message");
        if (!msgEl) {
            msgEl = document.createElement("p");
            msgEl.className = "sn-promo-message";
            if (promoForm) promoForm.appendChild(msgEl);
        }

        /* backend */

        // Codes démo frontend
        var PROMO_CODES = {
            "SNEAKERS10": { type: "percent", value: 10, msg: "10% de réduction appliquée !" },
            "SUMMER20":   { type: "percent", value: 20, msg: "20% de réduction Summer Sale !" },
            "FLAT15":     { type: "fixed",   value: 15, msg: "$15 de réduction appliquée !" },
        };

        var promo = PROMO_CODES[code];

        if (!promo) {
            msgEl.textContent   = "Code invalide ou expiré.";
            msgEl.className     = "sn-promo-message sn-promo-message--error";
            return;
        }

        // Calcule la remise
        var subtotalEl   = document.querySelector(".sn-order-subtotal");
        var subtotal     = subtotalEl ? parsePrice(subtotalEl.textContent) : 0;
        var discountAmt  = promo.type === "percent"
                            ? (subtotal * promo.value / 100)
                            : promo.value;

        // Stocke la remise dans le DOM
        var discountDisplay = document.querySelector(".sn-promo-discount");
        if (!discountDisplay) {
            discountDisplay = document.createElement("span");
            discountDisplay.className = "sn-promo-discount";
            discountDisplay.style.display = "none";
        }
        discountDisplay.textContent = formatPrice(discountAmt);
        document.body.appendChild(discountDisplay);

        msgEl.textContent   = promo.msg;
        msgEl.className     = "sn-promo-message sn-promo-message--success";
        input.value         = "";
        input.disabled      = true;
    }

    // PANIER VIDE
    function checkEmptyCart() {
        var items    = cartSection.querySelectorAll(".sn-cart-item");
        var emptyMsg = document.querySelector(".sn-cart-empty");

        if (!items.length) {
            var cartItems = document.querySelector(".sn-cart-items");
            var emptyTemplate = document.getElementById("sn-cart-empty-template");
            if (cartItems && !emptyMsg && emptyTemplate) {
                // Cloné depuis un gabarit rendu (et traduit) côté serveur, plutôt
                // que du texte en dur ici, pour rester correct dans les 3 langues.
                cartItems.innerHTML = emptyTemplate.innerHTML;
            }

            // Désactive le bouton checkout
            var checkoutBtn = document.querySelector(".sn-checkout-btn");
            if (checkoutBtn) {
                checkoutBtn.disabled = true;
                if (checkoutBtn.dataset.emptyLabel) {
                    checkoutBtn.textContent = checkoutBtn.dataset.emptyLabel;
                }
            }
        }
    }

    // BADGE PANIER (header, présent sur toutes les pages)
    function updateCartBadge(count) {
        var badge = document.querySelector(".sn-cart-count");
        if (!badge) return;

        badge.textContent   = count;
        badge.style.display = count > 0 ? "flex" : "none";

        badge.classList.remove("sn-cart-count--bump");
        void badge.offsetWidth;
        badge.classList.add("sn-cart-count--bump");
    }

    // SYNC BACKEND — vrai panier Odoo (sale.order via /cart/update_line)
    function syncWithBackend(cartItem, qty) {
        var lineId = cartItem.dataset.lineId;
        if (!lineId) return;

        jsonRpc("/cart/update_line", { line_id: lineId, qty: qty }).then(function (data) {
            if (!data || data.error) return;
            var totalEl = cartItem.querySelector(".sn-cart-total");
            if (totalEl && data.line_total_html) totalEl.innerHTML = data.line_total_html;
            applyCartTotals(data);
        });
    }

    function removeLineBackend(lineId) {
        return jsonRpc("/cart/remove_line", { line_id: lineId });
    }

    function jsonRpc(url, params) {
        return fetch(url, {
            method: "POST",
            headers: { "Content-Type": "application/json" },
            body: JSON.stringify({ jsonrpc: "2.0", method: "call", params: params }),
        })
            .then(function (r) { return r.json(); })
            .then(function (data) { return data.result; });
    }

    function parsePrice(str) {
        return parseFloat((str || "0").replace(/[^0-9.]/g, "")) || 0;
    }

    function formatPrice(amount) {
        return "$" + amount.toFixed(2);
    }

    function setHtmlIfExists(selector, html) {
        var el = document.querySelector(selector);
        if (el && html != null) el.innerHTML = html;
    }

    //Initialisation
    checkEmptyCart();

})();
