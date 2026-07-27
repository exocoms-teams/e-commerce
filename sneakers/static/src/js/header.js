(function () {

    // HEADER STICKY
    var header = document.querySelector(".sn-header");

    if (header) {
        var STICKY_THRESHOLD = 80;

        window.addEventListener("scroll", function () {
            if (window.scrollY > STICKY_THRESHOLD) {
                header.classList.add("sn-header--sticky");
            } else {
                header.classList.remove("sn-header--sticky");
            }
        }, { passive: true });
    }

    // MENU HAMBURGER (mobile)
    var nav = document.querySelector(".sn-nav");

    if (nav && !document.querySelector(".sn-hamburger")) {
        var hamburger = document.createElement("button");
        hamburger.className  = "sn-hamburger";
        hamburger.setAttribute("aria-label", "Toggle navigation");
        hamburger.setAttribute("aria-expanded", "false");
        hamburger.innerHTML  =
            '<span></span><span></span><span></span>';

        var headerInner = document.querySelector(".sn-header .mn-container");
        if (headerInner) {
            headerInner.insertBefore(hamburger, nav);
        }

        hamburger.addEventListener("click", function () {
            var isOpen = nav.classList.toggle("sn-nav--open");
            hamburger.classList.toggle("sn-hamburger--active", isOpen);
            hamburger.setAttribute("aria-expanded", isOpen ? "true" : "false");

            document.body.style.overflow = isOpen ? "hidden" : "";
        });

        document.addEventListener("click", function (e) {
            if (
                nav.classList.contains("sn-nav--open") &&
                !nav.contains(e.target) &&
                !hamburger.contains(e.target)
            ) {
                nav.classList.remove("sn-nav--open");
                hamburger.classList.remove("sn-hamburger--active");
                hamburger.setAttribute("aria-expanded", "false");
                document.body.style.overflow = "";
            }
        });

        document.addEventListener("keydown", function (e) {
            if (e.key === "Escape" && nav.classList.contains("sn-nav--open")) {
                nav.classList.remove("sn-nav--open");
                hamburger.classList.remove("sn-hamburger--active");
                hamburger.setAttribute("aria-expanded", "false");
                document.body.style.overflow = "";
            }
        });
    }

    // SÉLECTEUR DE LANGUE
    var languageSwitcher = document.querySelector(".sn-language-switcher");

    if (languageSwitcher) {
        languageSwitcher.addEventListener("change", function () {
            var selectedLang = this.value;
            console.log("[header.js] Langue sélectionnée :", selectedLang);
        });
    }

    (function initCartBadge() {
        var cart = JSON.parse(localStorage.getItem('sn_cart') || '[]');
        var count = cart.reduce(function(acc, item) { return acc + (item.qty || 1); }, 0);
        var badge = document.querySelector('.sn-cart-count');
        if (!badge) return;
        badge.textContent = count;
        badge.style.display = count > 0 ? 'flex' : 'none';
    })();

    (function initWishlistBadge() {
        var wl = JSON.parse(localStorage.getItem('sn_wishlist') || '[]');
        var badge = document.querySelector('.sn-wishlist-count');
        if (!badge) return;
        badge.textContent = wl.length;
        badge.style.display = wl.length > 0 ? 'flex' : 'none';
    })();

    document.addEventListener("click", function(e) {
        var btn = e.target.closest(".sn-add-cart");
        if (!btn) return;
        e.preventDefault();

        var productId = btn.dataset.productId || "0";
        var productName = btn.dataset.productName || "Produit";
        var qty = 1;

        // Lire et mettre à jour le panier localStorage
        var cart = JSON.parse(localStorage.getItem('sn_cart') || '[]');
        var existing = cart.find(function(i) { return i.productId === productId; });
        if (existing) {
            existing.qty += qty;
        } else {
            cart.push({ productId: productId, name: productName, qty: qty });
        }
        localStorage.setItem('sn_cart', JSON.stringify(cart));

        // Mettre à jour le badge
        var count = cart.reduce(function(acc, i) { return acc + i.qty; }, 0);
        var badge = document.querySelector('.sn-cart-count');
        if (badge) {
            badge.textContent = count;
            badge.style.display = 'flex';
            badge.classList.remove('sn-cart-count--bump');
            void badge.offsetWidth;
            badge.classList.add('sn-cart-count--bump');
        }

        // Feedback visuel
        var orig = btn.textContent;
        btn.textContent = "✓ Added!";
        btn.disabled = true;
        setTimeout(function() { btn.textContent = orig; btn.disabled = false; }, 1800);

        if (window.snShowToast) window.snShowToast("Produit ajouté au panier !");

        /* BACKEND : appeler /shop/cart/update avec product_id et qty */
    });

})();