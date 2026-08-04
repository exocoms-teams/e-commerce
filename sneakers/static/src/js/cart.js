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
    // ================================================
    // SYNC CART DATA FROM DOM (reads current state)
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

        badge.textContent = count;

        // Toujours afficher le badge même avec 0
        badge.style.display = "flex";

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
    // EMPTY CART UI
    // ================================================

    function handleEmptyCartUI(){

        if(cartSection.querySelector(".sn-cart-item")){
            return;
        }


        var summaryCard = document.querySelector(".sn-summary-card");
        if(summaryCard){
            summaryCard.style.display = "none";
        }



        var checkoutBtn = document.querySelector(".sn-checkout-btn");
        if(checkoutBtn){
            checkoutBtn.disabled = true;
            checkoutBtn.textContent = "Empty cart";
        }


        var cartLayout = document.querySelector(".sn-cart-layout");
        if(cartLayout){
            cartLayout.style.gridTemplateColumns = "1fr";
        }


        var cartTitle = document.querySelector(".sn-cart-header h2");
        if(cartTitle){
            cartTitle.style.display = "none";
        }


        var cartSubtitle = document.querySelector(".sn-cart-header p");
        if(cartSubtitle){
            cartSubtitle.style.display = "none";
        }

    }

    handleEmptyCartUI();
    cartSection.querySelectorAll(".sn-cart-item").forEach(function(item){

        updateIncreaseButtonState(item);

    });


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

            var stock = parseInt(
                input.dataset.stock,
                10
            );


            console.log("CART PRODUCT STOCK :", stock);


            if (isNaN(stock) || stock <= 0 || current >= stock) {

                if(window.snShowToast){

                    window.snShowToast(
                        stock <= 0 
                        ? "Produit indisponible"
                        : "Maximum disponible : " + stock + " article(s)",
                        "error"
                    );

                }

                return;
            }


            input.value = current + 1;
            updateIncreaseButtonState(cartItem);
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


    // Active ou désactive le bouton d'augmentation de quantité
    // selon le stock disponible du produit.
    // Le bouton "+" est bloqué lorsque la quantité sélectionnée
    // atteint la quantité maximale disponible en stock.
    
    function updateIncreaseButtonState(cartItem){

    var input = cartItem.querySelector(".sn-cart-qty-input");

    var increaseBtn = cartItem.querySelector(
        ".sn-qty-btn[data-action='increase']"
    );


    if(!input || !increaseBtn){
        return;
    }


    var stock = parseInt(
        input.dataset.stock,
        10
    );


    var qty = parseInt(
        input.value,
        10
    );


    if(qty >= stock){

        increaseBtn.disabled = true;

    }else{

        increaseBtn.disabled = false;

    }

}

    // ================================================
    // SAISIE DIRECTE DANS L'INPUT
    // ================================================

    cartSection.addEventListener("change", function (e) {
        if (e.target.type !== "number") return;

        var cartItem = e.target.closest(".sn-cart-item");
        if (!cartItem) return;

        var val = parseInt(e.target.value, 10);

        var stock = parseInt(
            e.target.dataset.stock,
            10
        );


        if (isNaN(val) || val < 1) {

            e.target.value = 1;
            val = 1;

        }


        if(!isNaN(stock) && val > stock){

            e.target.value = stock;
            val = stock;


            if(window.snShowToast){

                window.snShowToast(
                    "Maximum disponible : " + stock + " article(s)",
                    "error"
                );

            }

        }

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

        handleEmptyCartUI();

    }

    },300);


});

})();