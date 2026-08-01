(function () {

    var wishlistSection = document.querySelector(".sn-wishlist");
    if (!wishlistSection) return;

    //SUPPRIMER UN ARTICLE DE LA WISHLIST
    wishlistSection.addEventListener("click", function (e) {

        var removeBtn = e.target.closest(".sn-wishlist-remove, .sn-remove-wishlist");
        if (!removeBtn) return;

        var wishlistItem = removeBtn.closest(".sn-wishlist-item, .sn-product-card");
        if (!wishlistItem) return;

        var productId = wishlistItem.dataset.productId || "0";

        // Animation de sortie
        wishlistItem.style.transition = "opacity 0.3s, transform 0.3s";
        wishlistItem.style.opacity    = "0";
        wishlistItem.style.transform  = "scale(0.9)";

        /* backend */

        // Frontend : met à jour localStorage
        removeFromLocalWishlist(productId);

        setTimeout(function () {
            wishlistItem.remove();
            checkEmptyWishlist();
        }, 300);
    });

    // AJOUTER AU PANIER DEPUIS LA WISHLIST
    wishlistSection.addEventListener("click", function (e) {

        var addBtn = e.target.closest(".sn-wishlist-add-cart, .sn-add-to-cart");
        if (!addBtn) return;

        var wishlistItem = addBtn.closest(".sn-wishlist-item, .sn-product-card");
        var productId    = wishlistItem ? (wishlistItem.dataset.productId || "0") : "0";

        var originalText = addBtn.textContent;
        addBtn.textContent = "Adding...";
        addBtn.disabled    = true;

        /* backend */

        // Simulation frontend 
        setTimeout(function () {
            addBtn.textContent = "✓ Added!";
            addBtn.classList.add("sn-btn--success");

            // Met à jour le badge panier dans le header
            var badge = document.querySelector(".sn-cart-count");
            if (badge) {
                var count = (parseInt(badge.textContent, 10) || 0) + 1;
                badge.textContent   = count;
                badge.style.display = "flex";
                badge.classList.remove("sn-cart-count--bump");
                void badge.offsetWidth;
                badge.classList.add("sn-cart-count--bump");
            }

            if (window.snShowToast) window.snShowToast("Produit ajouté au panier !");

            setTimeout(function () {
                addBtn.textContent = originalText;
                addBtn.disabled    = false;
                addBtn.classList.remove("sn-btn--success");
            }, 2000);
        }, 600);
    });


    function checkEmptyWishlist() {
        var items = wishlistSection.querySelectorAll(".sn-wishlist-item, .sn-product-card");

        if (!items.length) {
            var grid = wishlistSection.querySelector(".sn-wishlist-grid, .sn-products-grid");
            if (grid) {
                grid.innerHTML =
                    '<div class="sn-wishlist-empty">' +
                        '<i class="fa fa-heart-o"></i>' +
                        '<h3>Votre wishlist est vide</h3>' +
                        '<p>Explorez notre catalogue et sauvegardez vos sneakers préférées.</p>' +
                        '<a href="/shop" class="sn-btn-primary">Parcourir le catalogue</a>' +
                    '</div>';
            }
        }
    }

    document.addEventListener("click", function (e) {
        var heartBtn = e.target.closest(".sn-product-wishlist, .sn-btn-heart");
        if (!heartBtn) return;

        e.preventDefault();

        var productId = heartBtn.dataset.productId || "0";
        var wl        = getLocalWishlist();
        var idx       = wl.indexOf(productId);

        if (idx !== -1) {
            wl.splice(idx, 1);
            heartBtn.classList.remove("active", "sn-btn-heart--active");
            heartBtn.setAttribute("aria-pressed", "false");
            if (window.snShowToast) window.snShowToast("Retiré de la wishlist");
        } else {
            wl.push(productId);
            heartBtn.classList.add("active", "sn-btn-heart--active");
            heartBtn.setAttribute("aria-pressed", "true");
            if (window.snShowToast) window.snShowToast("Ajouté à la wishlist !");
        }

        saveLocalWishlist(wl);

        // Mettre à jour le badge wishlist dans le header
        var wlBadge = document.querySelector('.sn-wishlist-count');
        if (wlBadge) {
            var newWl = getLocalWishlist();
            wlBadge.textContent = newWl.length;
            wlBadge.style.display = 'flex';
        }

        /* backend */
    });

    // UTILITAIRES localStorage 
    function getLocalWishlist() {
        try { return JSON.parse(localStorage.getItem("sn_wishlist") || "[]"); }
        catch (e) { return []; }
    }

    function saveLocalWishlist(wl) {
        try { localStorage.setItem("sn_wishlist", JSON.stringify(wl)); }
        catch (e) { /* ignorer */ }
    }

    function removeFromLocalWishlist(productId) {
        var wl = getLocalWishlist();
        var filtered = wl.filter(function (id) { return id !== productId; });
        saveLocalWishlist(filtered);
    }

    function initHeartStates() {
        var wl = getLocalWishlist();
        document.querySelectorAll(".sn-product-wishlist, .sn-btn-heart").forEach(function (btn) {
            var id = btn.dataset.productId || "0";
            if (wl.indexOf(id) !== -1) {
                btn.classList.add("active", "sn-btn-heart--active");
                btn.setAttribute("aria-pressed", "true");
            }
        });
    }

    initHeartStates();
    checkEmptyWishlist();

})();
