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
        updateCartTotals();
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
        updateCartTotals();
        syncWithBackend(cartItem, val);
    });

    // SUPPRESSION D'UN ARTICLE
    cartSection.addEventListener("click", function (e) {

        var removeBtn = e.target.closest(".sn-cart-remove");
        if (!removeBtn) return;

        var cartItem = removeBtn.closest(".sn-cart-item");
        if (!cartItem) return;

        // Animation de sortie
        cartItem.style.transition = "opacity 0.3s, transform 0.3s";
        cartItem.style.opacity    = "0";
        cartItem.style.transform  = "translateX(40px)";

        /* backend */

        setTimeout(function () {
            cartItem.remove();
            updateCartTotals();
            checkEmptyCart();
        }, 300);
    });

    // CALCUL TOTAL PAR ARTICLE 
    function updateItemTotal(cartItem, qty) {
        var priceEl = cartItem.querySelector(".sn-cart-price");
        var totalEl = cartItem.querySelector(".sn-cart-total");
        if (!priceEl || !totalEl) return;

        var price = parsePrice(priceEl.textContent);
        var total = price * parseInt(qty, 10);

        totalEl.textContent = formatPrice(total);
    }

    // CALCUL TOTAUX GÉNÉRAUX
    function updateCartTotals() {
        var items        = cartSection.querySelectorAll(".sn-cart-item");
        var subtotal     = 0;

        items.forEach(function (item) {
            var input    = item.querySelector("input[type='number']");
            var priceEl  = item.querySelector(".sn-cart-price");
            if (!input || !priceEl) return;

            var price = parsePrice(priceEl.textContent);
            var qty   = parseInt(input.value, 10) || 1;
            subtotal += price * qty;
        });

        // Livraison
        var shippingRate  = subtotal >= 100 ? 0 : 15;
        var discount      = getAppliedDiscount();
        var total         = Math.max(0, subtotal - discount + shippingRate);
        var itemCount     = Array.from(items).reduce(function (acc, item) {
            var input = item.querySelector("input[type='number']");
            return acc + (input ? parseInt(input.value, 10) || 1 : 1);
        }, 0);

        // Mise à jour DOM
        setTextIfExists(".sn-order-subtotal",  formatPrice(subtotal));
        setTextIfExists(".sn-order-shipping",  shippingRate === 0 ? "Free" : formatPrice(shippingRate));
        setTextIfExists(".sn-order-discount",  discount > 0 ? "-" + formatPrice(discount) : "-");
        setTextIfExists(".sn-order-total",     formatPrice(total));

        // Badge panier dans le header
        updateCartBadge(itemCount);
    }

    function getAppliedDiscount() {
        var discountEl = document.querySelector(".sn-promo-discount");
        return discountEl ? parsePrice(discountEl.textContent) : 0;
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

        updateCartTotals();
    }

    // PANIER VIDE
    function checkEmptyCart() {
        var items    = cartSection.querySelectorAll(".sn-cart-item");
        var emptyMsg = document.querySelector(".sn-cart-empty");

        if (!items.length) {
            var cartItems = document.querySelector(".sn-cart-items");
            if (cartItems && !emptyMsg) {
                cartItems.innerHTML =
                    '<div class="sn-cart-empty">' +
                        '<i class="fa fa-shopping-cart"></i>' +
                        '<h3>Your cart is empty</h3>' +
                        '<p>Browse our catalog and add your favorite sneakers.</p>' +
                        '<a href="/shop-sneakers" class="sn-btn-primary">Continue Shopping</a>' +
                    '</div>';
            }
            // masquer l'order summary
            var summaryCard = document.querySelector(".sn-summary-card");
            if (summaryCard) summaryCard.style.display = "none";
            //Masquer la promo card si elle existe
            var promoCard = document.querySelector(".sn-promo-card");
            if (promoCard) promoCard.style.display = "none";
            // Désactive le bouton checkout
            var checkoutBtn = document.querySelector(".sn-checkout-btn");
            if (checkoutBtn) {
                checkoutBtn.disabled = true;
                checkoutBtn.textContent = "Empty cart";
            }
            
        }

        updateCartTotals();
    }

    // BADGE PANIER 
    function updateCartBadge(count) {
        var badge = document.querySelector(".sn-cart-count");
        if (!badge) return;

        badge.textContent   = count;
        badge.style.display = count > 0 ? "flex" : "none";

        badge.classList.remove("sn-cart-count--bump");
        void badge.offsetWidth;
        badge.classList.add("sn-cart-count--bump");
    }

    // SYNC BACKEND 
    function syncWithBackend(cartItem, qty) {
        var productId = cartItem.dataset.productId || "0";
        /* backend */
        console.log("[cart.js] Sync backend : productId=" + productId + ", qty=" + qty);
    }

    function parsePrice(str) {
        return parseFloat((str || "0").replace(/[^0-9.]/g, "")) || 0;
    }

    function formatPrice(amount) {
        return "$" + amount.toFixed(2);
    }

    function setTextIfExists(selector, text) {
        var el = document.querySelector(selector);
        if (el) el.textContent = text;
    }

    //Initialisation
    updateCartTotals();

})();
