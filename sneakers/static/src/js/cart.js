(function () {

    function parsePrice(str) {
        return parseFloat((str || "0").replace(/[^0-9.]/g, "")) || 0;
    }

    function formatPrice(amount) {
        return "$" + parseFloat(amount || 0).toFixed(2);
    }

    function setTextIfExists(selector, text) {
        var el = document.querySelector(selector);
        if (el) el.textContent = text;
    }

    function getCart() {
        try { return JSON.parse(localStorage.getItem("sn_cart") || "[]"); }
        catch (e) { return []; }
    }

    function saveCart(cart) {
        localStorage.setItem("sn_cart", JSON.stringify(cart));
    }

    function getAppliedDiscount() {
        try { return parseFloat(localStorage.getItem("sn_discount") || "0") || 0; }
        catch (e) { return 0; }
    }

    // RENDU DES ARTICLES DEPUIS LOCALSTORAGE
    function renderCartItems() {
        var cartItemsWrapper = document.querySelector(".sn-cart-items");
        if (!cartItemsWrapper) return;

        var cart = getCart();

        cartItemsWrapper.innerHTML = "";

        if (!cart.length) {
            cartItemsWrapper.innerHTML =
                '<div class="sn-cart-empty">' +
                    '<i class="fa fa-shopping-cart"></i>' +
                    '<h3>Your cart is empty</h3>' +
                    '<p>Browse our catalog and add your favorite sneakers.</p>' +
                    '<a href="/shop-sneakers" class="sn-btn-primary">Continue Shopping</a>' +
                '</div>';

            var summaryCard = document.querySelector(".sn-summary-card");
            if (summaryCard) summaryCard.style.display = "none";

            var promoCard = document.querySelector(".sn-promo-card");
            if (promoCard) promoCard.style.display = "none";

            var checkoutBtn = document.querySelector(".sn-checkout-btn");
            if (checkoutBtn) {
                checkoutBtn.disabled    = true;
                checkoutBtn.textContent = "Empty cart";
            }

            var cartLayout = document.querySelector(".sn-cart-layout");
            if (cartLayout) cartLayout.style.gridTemplateColumns = "1fr";

            var cartTitle = document.querySelector(".sn-cart-header h2");
            if (cartTitle) cartTitle.style.display = "none";
            
            var cartSubtitle = document.querySelector(".sn-cart-header p");
            if (cartSubtitle) cartSubtitle.style.display = "none";

            updateOrderSummary(cart);
            return;
        }

        // Afficher le summary si caché
        var summaryCard = document.querySelector(".sn-summary-card");
        if (summaryCard) summaryCard.style.display = "";

        var promoCard = document.querySelector(".sn-promo-card");
        if (promoCard) promoCard.style.display = "";

        cart.forEach(function (item) {
            var article = document.createElement("article");
            article.className         = "sn-cart-item";
            article.dataset.productId = item.productId;
            article.innerHTML =
                '<div class="sn-cart-image">' +
                    '<img src="' + (item.image || "") + '" alt="' + item.name + '"/>' +
                '</div>' +
                '<div class="sn-cart-info">' +
                    '<h3>' + item.name + '</h3>' +
                    '<div class="sn-cart-price">' + formatPrice(item.price) + '</div>' +
                '</div>' +
                '<div class="sn-cart-quantity">' +
                    '<button class="sn-qty-btn" data-action="decrease">-</button>' +
                    '<input type="number" value="' + item.qty + '" min="1"/>' +
                    '<button class="sn-qty-btn" data-action="increase">+</button>' +
                '</div>' +
                '<div class="sn-cart-total">' + formatPrice(item.price * item.qty) + '</div>' +
                '<button class="sn-cart-remove" aria-label="Supprimer">' +
                    '<i class="fa fa-trash"></i>' +
                '</button>';
            cartItemsWrapper.appendChild(article);
        });

        updateOrderSummary(cart);
    }

    // ORDER SUMMARY — totaux 
    function updateOrderSummary(cart) {
        var subtotal  = cart.reduce(function (acc, i) { return acc + i.price * i.qty; }, 0);
        var shipping  = subtotal > 0 && subtotal >= 100 ? 0 : (subtotal > 0 ? 15 : 0);
        var tax       = subtotal * 0.08; // 8% estimated tax
        var discount  = getAppliedDiscount();
        var total     = Math.max(0, subtotal - discount + shipping + tax);
        var itemCount = cart.reduce(function (acc, i) { return acc + i.qty; }, 0);

        setTextIfExists(".sn-order-subtotal", formatPrice(subtotal));
        setTextIfExists(".sn-order-shipping",  shipping === 0 ? (subtotal > 0 ? "Free" : formatPrice(0)) : formatPrice(shipping));
        setTextIfExists(".sn-order-tax",       formatPrice(tax));
        setTextIfExists(".sn-order-discount",  discount > 0 ? "-" + formatPrice(discount) : "-");
        setTextIfExists(".sn-order-total",     formatPrice(total));
        updateCartBadge(itemCount);
    }

    // SYNC DOM → LOCALSTORAGE (après +/- ou suppression)
    function syncCartFromDOM() {
        var items = cartSection.querySelectorAll(".sn-cart-item");
        var cart  = [];
        items.forEach(function (item) {
            var input   = item.querySelector("input[type='number']");
            var priceEl = item.querySelector(".sn-cart-price");
            var nameEl  = item.querySelector("h3");
            var imgEl   = item.querySelector("img");
            if (!input || !priceEl) return;
            cart.push({
                productId : item.dataset.productId || "0",
                name      : nameEl  ? nameEl.textContent.trim() : "",
                price     : parsePrice(priceEl.textContent),
                image     : imgEl   ? imgEl.src : "",
                qty       : parseInt(input.value, 10) || 1
            });
        });
        saveCart(cart);
        updateOrderSummary(cart);
    }

    // CALCUL TOTAL PAR ARTICLE (mise à jour DOM)
    function updateItemTotal(cartItem, qty) {
        var priceEl = cartItem.querySelector(".sn-cart-price");
        var totalEl = cartItem.querySelector(".sn-cart-total");
        if (!priceEl || !totalEl) return;
        var price = parsePrice(priceEl.textContent);
        totalEl.textContent = formatPrice(price * parseInt(qty, 10));
    }

    // BADGE HEADER
    function updateCartBadge(count) {
        var badge = document.querySelector(".sn-cart-count");
        if (!badge) return;
        badge.textContent   = count;
        badge.style.display = "flex";
        badge.classList.remove("sn-cart-count--bump");
        void badge.offsetWidth;
        badge.classList.add("sn-cart-count--bump");
    }

    // INITIALISATION

    var cartSection = document.querySelector(".sn-cart");
    if (!cartSection) return;

    // Rendre les articles depuis localStorage au chargement
    renderCartItems();

    // BOUTONS +/- QUANTITÉ

    cartSection.addEventListener("click", function (e) {
        var btn = e.target.closest(".sn-qty-btn");
        if (!btn) return;

        var cartItem = btn.closest(".sn-cart-item");
        if (!cartItem) return;

        var input = cartItem.querySelector("input[type='number']");
        if (!input) return;

        var current = parseInt(input.value, 10) || 1;

        if (btn.textContent.trim() === "+" || btn.dataset.action === "increase") {
            input.value = current + 1;
        } else if (btn.textContent.trim() === "-" || btn.dataset.action === "decrease") {
            if (current > 1) input.value = current - 1;
        }

        updateItemTotal(cartItem, input.value);
        syncCartFromDOM();
    });

    // SAISIE DIRECTE DANS L'INPUT
    cartSection.addEventListener("change", function (e) {
        if (e.target.type !== "number") return;

        var cartItem = e.target.closest(".sn-cart-item");
        if (!cartItem) return;

        var val = parseInt(e.target.value, 10);
        if (isNaN(val) || val < 1) { e.target.value = 1; val = 1; }

        updateItemTotal(cartItem, val);
        syncCartFromDOM();
    });

    // SUPPRESSION D'UN ARTICLE
    cartSection.addEventListener("click", function (e) {
        var removeBtn = e.target.closest(".sn-cart-remove");
        if (!removeBtn) return;

        var cartItem = removeBtn.closest(".sn-cart-item");
        if (!cartItem) return;

        cartItem.style.transition = "opacity 0.3s, transform 0.3s";
        cartItem.style.opacity    = "0";
        cartItem.style.transform  = "translateX(40px)";

        /* BACKEND — supprimer la ligne dans sale.order */

        setTimeout(function () {
            cartItem.remove();
            syncCartFromDOM();

            // Si panier vide après suppression, re-rendre l'état vide
            if (!cartSection.querySelectorAll(".sn-cart-item").length) {
                renderCartItems();
            }
        }, 300);
    });

    // CODE PROMO
    var promoForm = document.querySelector(".sn-promo-form");
    if (promoForm) {
        var PROMO_CODES = {
            "SNEAKERS10": { type: "percent", value: 10, msg: "10% discount applied!" },
            "SUMMER20":   { type: "percent", value: 20, msg: "20% Summer Sale discount!" },
            "FLAT15":     { type: "fixed",   value: 15, msg: "$15 discount applied!" }
        };

        function applyPromoCode() {
            var promoInput = promoForm.querySelector("input[type='text']");
            if (!promoInput) return;

            var code  = promoInput.value.trim().toUpperCase();
            if (!code) return;

            var msgEl = document.querySelector(".sn-promo-message");
            if (!msgEl) {
                msgEl = document.createElement("p");
                msgEl.className = "sn-promo-message";
                promoForm.appendChild(msgEl);
            }

            /* BACKEND — valider le code promo */

            var promo = PROMO_CODES[code];
            if (!promo) {
                msgEl.textContent = "Invalid or expired code.";
                msgEl.className   = "sn-promo-message sn-promo-message--error";
                return;
            }

            var subtotal    = getCart().reduce(function (acc, i) { return acc + i.price * i.qty; }, 0);
            var discountAmt = promo.type === "percent"
                ? (subtotal * promo.value / 100)
                : promo.value;

            localStorage.setItem("sn_discount", discountAmt);

            msgEl.textContent    = promo.msg;
            msgEl.className      = "sn-promo-message sn-promo-message--success";
            promoInput.value     = "";
            promoInput.disabled  = true;

            updateOrderSummary(getCart());
        }

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

})();