(function () {

    // ================================================
    // UTILITAIRES
    // ================================================

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


    // ================================================
    // ORDER SUMMARY — totaux + liste articles sidebar
    // ================================================

    function updateOrderSummary(cart) {
        if (!cart) {
        cart = [];
        }
        var subtotal  = cart.reduce(function (acc, i) { return acc + i.price * i.qty; }, 0);
        var shipping  = subtotal > 0 && subtotal >= 100 ? 0 : (subtotal > 0 ? 15 : 0);
        var discount  = 0;
        var total     = Math.max(0, subtotal - discount + shipping);
        var itemCount = cart.reduce(function (acc, i) { return acc + i.qty; }, 0);

        setTextIfExists(".sn-order-subtotal", formatPrice(subtotal));
        setTextIfExists(".sn-order-shipping",  shipping === 0 ? (subtotal > 0 ? "Free" : formatPrice(0)) : formatPrice(shipping));
        setTextIfExists(".sn-order-discount",  discount > 0 ? "-" + formatPrice(discount) : "-");
        setTextIfExists(".sn-order-total",     formatPrice(total));

        // Liste des articles dans la sidebar du summary
        var summaryList = document.querySelector(".sn-order-items");
        if (summaryList) {
            summaryList.innerHTML = "";
            cart.forEach(function (item) {
                var row = document.createElement("div");
                row.className = "sn-order-item";
                row.innerHTML =
                    '<div class="sn-order-item-info">' +
                        (item.image
                            ? '<img src="' + item.image + '" alt="' + item.name + '" class="sn-order-item-img"/>'
                            : "") +
                        '<span class="sn-order-item-name">' + item.name + '</span>' +
                        '<span class="sn-order-item-qty">x' + item.qty + '</span>' +
                    '</div>' +
                    '<span class="sn-order-item-total">' + formatPrice(item.price * item.qty) + '</span>';
                summaryList.appendChild(row);
            });
        }

        updateCartBadge(itemCount);
    }

    // ================================================
    // SYNC DOM → LOCALSTORAGE (après +/- ou suppression)
    // ================================================

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
        updateOrderSummary(cart);
        return cart;
    }

    // ================================================
    // CALCUL TOTAL PAR ARTICLE (mise à jour DOM)
    // ================================================

    function updateItemTotal(cartItem, qty) {
        var priceEl = cartItem.querySelector(".sn-cart-price");
        var totalEl = cartItem.querySelector(".sn-cart-total");
        if (!priceEl || !totalEl) return;
        var price = parsePrice(priceEl.textContent);
        totalEl.textContent = formatPrice(price * parseInt(qty, 10));
    }

    // ================================================
    // BADGE HEADER
    // ================================================

    function updateCartBadge(count) {
        var badge = document.querySelector(".sn-cart-count");
        if (!badge) return;
        badge.textContent   = count;
        badge.style.display = count > 0 ? "flex" : "none";
        badge.classList.remove("sn-cart-count--bump");
        void badge.offsetWidth;
        badge.classList.add("sn-cart-count--bump");
    }

    // ================================================
// UPDATE CART ODOO BACKEND
// ================================================

function updateCartBackend(lineId, qty) {

    fetch('/shop/cart/update', {
        method: 'POST',
        credentials: 'include',
        headers: {
            'Content-Type': 'application/json',
        },
        body: JSON.stringify({
            jsonrpc: "2.0",
            method: "call",
            params: {
                line_id: parseInt(lineId),
                quantity: parseInt(qty)
            }
        })
    })
    .then(function(response){
        return response.json();
    })
    .catch(function(error){

        console.error("CART UPDATE ERROR :", error);

    });

}

    // ================================================
    // INITIALISATION
    // ================================================

    var cartSection = document.querySelector(".sn-cart");
    if (!cartSection) return;


    // ================================================
    // BOUTONS +/- QUANTITÉ
    // ================================================

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
        var lineId = cartItem.dataset.lineId;

        updateCartBackend(
            lineId,
            input.value
        );
        syncCartFromDOM();
    });



    // ================================================
    // SAISIE DIRECTE DANS L'INPUT
    // ================================================

    cartSection.addEventListener("change", function (e) {
        if (e.target.type !== "number") return;

        var cartItem = e.target.closest(".sn-cart-item");
        if (!cartItem) return;

        var val = parseInt(e.target.value, 10);
        if (isNaN(val) || val < 1) { e.target.value = 1; val = 1; }

        updateItemTotal(cartItem, val);


        var lineId = cartItem.dataset.lineId;
        var productId = cartItem.dataset.productId;

        updateCartBackend(
            lineId,
            val
        );


        syncCartFromDOM();
    });

    // ================================================
// SUPPRESSION D'UN ARTICLE
// ================================================

cartSection.addEventListener("click", function (e) {

    var removeBtn = e.target.closest(".sn-cart-remove");

    if (!removeBtn) return;


    var cartItem = removeBtn.closest(".sn-cart-item");

    if (!cartItem) return;


    var lineId = cartItem.dataset.lineId;
    var productId = cartItem.dataset.productId;


    // suppression côté Odoo
    updateCartBackend(lineId, 0);


    cartItem.style.opacity = "0";


    setTimeout(function(){

        cartItem.remove();


        syncCartFromDOM();


        if (!cartSection.querySelector(".sn-cart-item")) {

            document.querySelector(".sn-cart-items").innerHTML =
            `
            <div class="sn-cart-empty">
                <i class="fa fa-shopping-cart"></i>
                <h3>Your cart is empty</h3>
                <p>Browse our catalog and add your favorite sneakers.</p>
                <a href="/shop-sneakers" class="sn-btn-primary">
                    Continue Shopping
                </a>
            </div>
            `;


            updateCartBadge(0);

        }

    },300);


});

    // ================================================
    // CODE PROMO
    // ================================================

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

            var cart = [];

            cartSection.querySelectorAll(".sn-cart-item").forEach(function(item){

                var price = parsePrice(
                    item.querySelector(".sn-cart-price").textContent
                );

                var qty = parseInt(
                    item.querySelector("input[type='number']").value,
                    10
                ) || 1;

                cart.push({
                    price: price,
                    qty: qty
                });

            });


            var subtotal = cart.reduce(function(acc, i){
                return acc + i.price * i.qty;
            }, 0);


            var discountAmt = promo.type === "percent"
                ? (subtotal * promo.value / 100)
                : promo.value;
            window.sn_discount = discountAmt;
            msgEl.textContent    = promo.msg;
            msgEl.className      = "sn-promo-message sn-promo-message--success";
            promoInput.value     = "";
            promoInput.disabled  = true;

            updateOrderSummary(syncCartFromDOM());
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