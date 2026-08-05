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

    // ============================
    // MENU HAMBURGER (mobile)
    // ============================
    (function initMobileNav() {
        var nav = document.querySelector(".sn-nav");
        if (!nav) return;

        var headerInner = document.querySelector(".sn-header .mn-container");
        if (!headerInner) return;

        var overlay = document.createElement("div");
        overlay.className = "sn-nav-overlay";
        overlay.setAttribute("aria-hidden", "true");
        document.body.appendChild(overlay);

        var navHeader = document.createElement("div");
        navHeader.className = "sn-nav-header";
        navHeader.innerHTML =
            '<span class="sn-nav-title">Menu</span>' +
            '<button type="button" class="sn-nav-close" aria-label="Fermer le menu">' +
            '<i class="fa fa-times" aria-hidden="true"></i></button>';
        nav.insertBefore(navHeader, nav.firstChild);

        var closeBtn = navHeader.querySelector(".sn-nav-close");

        var hamburger = document.createElement("button");
        hamburger.type = "button";
        hamburger.className = "sn-hamburger";
        hamburger.setAttribute("aria-label", "Ouvrir le menu");
        hamburger.setAttribute("aria-expanded", "false");
        hamburger.innerHTML = "<span></span><span></span><span></span>";

        headerInner.insertBefore(hamburger, nav);

        function openNav() {
            nav.classList.add("sn-nav--open");
            overlay.classList.add("sn-nav-overlay--visible");
            overlay.setAttribute("aria-hidden", "false");
            hamburger.setAttribute("aria-expanded", "true");
            document.body.style.overflow = "hidden";
        }

        function closeNav() {
            nav.classList.remove("sn-nav--open");
            overlay.classList.remove("sn-nav-overlay--visible");
            overlay.setAttribute("aria-hidden", "true");
            hamburger.setAttribute("aria-expanded", "false");
            document.body.style.overflow = "";
        }

        hamburger.addEventListener("click", function () {
            if (!nav.classList.contains("sn-nav--open")) {
                openNav();
            }
        });

        closeBtn.addEventListener("click", closeNav);
        overlay.addEventListener("click", closeNav);

        document.addEventListener("keydown", function (e) {
            if (e.key === "Escape" && nav.classList.contains("sn-nav--open")) {
                closeNav();
            }
        });
    })();


    // SÉLECTEUR DE LANGUE
    var languageSwitcher = document.querySelector(".sn-language-switcher");

    if (languageSwitcher) {
        languageSwitcher.addEventListener("change", function () {
            var selectedLang = this.value;
            console.log("[header.js] Langue sélectionnée :", selectedLang);
        });
    }

    (function initCartBadge() {

        var badge = document.querySelector('.sn-cart-count');

        if (!badge) return;


        fetch('/shop/cart/quantity', {

            method: 'POST',

            headers: {
                'Content-Type': 'application/json',
            },

            body: JSON.stringify({
                jsonrpc: "2.0",
                method: "call",
                params: {}
            })

        })
        .then(function(response){

            return response.json();

        })
        .then(function(data){

            console.log("ODOO CART QUANTITY :", data);


            var quantity = data.result || 0;


            if(quantity > 0){

                badge.textContent = quantity;
                badge.style.display = 'flex';

            }else{

                badge.style.display = 'none';

            }

        })
        .catch(function(error){

            console.error("CART BADGE ERROR", error);

        });


    })();

    (function initWishlistBadge() {
        var wl = JSON.parse(localStorage.getItem('sn_wishlist') || '[]');
        var badge = document.querySelector('.sn-wishlist-count');
        if (!badge) return;
        badge.textContent = wl.length;
        badge.style.display = wl.length > 0 ? 'flex' : 'none';
    })();

    /* BACKEND : appeler /shop/cart/update avec product_id , qty */

})();
