(function () {

    var productSection = document.querySelector(".sn-product-details");
    if (!productSection) return;

    initGallery();
    
    initSizeSelection();

    initColorSelection();

    initQuantitySelector();

    initAddToCartProduct();

    initTabs();

    initWishlistToggle();

    // GALERIE PRODUIT
    function initGallery() {

        var mainImg     = document.querySelector(".sn-product-main-image img");
        var thumbsWrap  = document.querySelector(".sn-product-thumbnails");
        if (!mainImg || !thumbsWrap) return;

        var thumbs = thumbsWrap.querySelectorAll(".sn-product-thumb");

        thumbs.forEach(function (thumb, i) {
            thumb.addEventListener("click", function () {
                var src = thumb.querySelector("img").src;
                var alt = thumb.querySelector("img").alt;

                mainImg.src = src;
                mainImg.alt = alt;

                thumbs.forEach(function (t) { t.classList.remove("active"); });
                thumb.classList.add("active");

                currentGalleryIndex = i;
            });
        });

        var allImages = [];
        thumbs.forEach(function (t) {
            allImages.push({ src: t.querySelector("img").src, alt: t.querySelector("img").alt });
        });

        var currentGalleryIndex = 0;

        var mainWrapper = document.querySelector(".sn-product-main-image");
        if (mainWrapper) {

            mainWrapper.style.overflow = "hidden";
            mainWrapper.style.cursor   = "zoom-in";

            mainImg.addEventListener("mousemove", function (e) {
                var rect   = mainWrapper.getBoundingClientRect();
                var xPct   = ((e.clientX - rect.left) / rect.width)  * 100;
                var yPct   = ((e.clientY - rect.top)  / rect.height) * 100;

                mainImg.style.transformOrigin = xPct + "% " + yPct + "%";
                mainImg.style.transform       = "scale(2)";
                mainImg.style.transition      = "transform 0.1s";
            });

            mainImg.addEventListener("mouseleave", function () {
                mainImg.style.transform = "scale(1)";
            });

            mainImg.addEventListener("click", function () {
                openLightbox(currentGalleryIndex, allImages);
            });
            mainWrapper.style.cursor = "zoom-in";
        }

        var touchStartX = 0;
        if (mainWrapper) {
            mainWrapper.addEventListener("touchstart", function (e) {
                touchStartX = e.changedTouches[0].screenX;
            }, { passive: true });

            mainWrapper.addEventListener("touchend", function (e) {
                var diff = touchStartX - e.changedTouches[0].screenX;
                if (Math.abs(diff) < 40) return;

                if (diff > 0) {
                    currentGalleryIndex = (currentGalleryIndex + 1) % allImages.length;
                } else {
                    currentGalleryIndex = (currentGalleryIndex - 1 + allImages.length) % allImages.length;
                }

                mainImg.src = allImages[currentGalleryIndex].src;
                mainImg.alt = allImages[currentGalleryIndex].alt;

                thumbs.forEach(function (t, i) {
                    t.classList.toggle("active", i === currentGalleryIndex);
                });
            }, { passive: true });
        }

        function openLightbox(index, images) {
            var lb = document.createElement("div");
            lb.className = "sn-lightbox";
            lb.setAttribute("role", "dialog");
            lb.setAttribute("aria-modal", "true");
            lb.setAttribute("aria-label", "Galerie produit plein écran");

            var currentIdx = index;

            function renderLightboxImg() {
                var imgEl = lb.querySelector(".sn-lightbox-img");
                if (imgEl) {
                    imgEl.src = images[currentIdx].src;
                    imgEl.alt = images[currentIdx].alt;
                }
                var counter = lb.querySelector(".sn-lightbox-counter");
                if (counter) counter.textContent = (currentIdx + 1) + " / " + images.length;
            }

            lb.innerHTML =
                '<button class="sn-lightbox-close" aria-label="Fermer">×</button>' +
                '<button class="sn-lightbox-prev" aria-label="Précédent">&#8249;</button>' +
                '<div class="sn-lightbox-content">' +
                    '<img class="sn-lightbox-img" src="" alt=""/>' +
                    '<span class="sn-lightbox-counter"></span>' +
                '</div>' +
                '<button class="sn-lightbox-next" aria-label="Suivant">&#8250;</button>';

            document.body.appendChild(lb);
            document.body.style.overflow = "hidden";
            renderLightboxImg();

            lb.querySelector(".sn-lightbox-close").addEventListener("click", closeLightbox);
            lb.addEventListener("click", function (e) {
                if (e.target === lb) closeLightbox();
            });

            lb.querySelector(".sn-lightbox-prev").addEventListener("click", function () {
                currentIdx = (currentIdx - 1 + images.length) % images.length;
                renderLightboxImg();
            });

            lb.querySelector(".sn-lightbox-next").addEventListener("click", function () {
                currentIdx = (currentIdx + 1) % images.length;
                renderLightboxImg();
            });

            document.addEventListener("keydown", lbKeydown);

            function lbKeydown(e) {
                if (e.key === "Escape")      closeLightbox();
                if (e.key === "ArrowRight") { currentIdx = (currentIdx + 1) % images.length; renderLightboxImg(); }
                if (e.key === "ArrowLeft")  { currentIdx = (currentIdx - 1 + images.length) % images.length; renderLightboxImg(); }
            }

            function closeLightbox() {
                lb.remove();
                document.body.style.overflow = "";
                document.removeEventListener("keydown", lbKeydown);
            }
        }
    }

    // SÉLECTION TAILLE 
    function initSizeSelection() {
        var sizeOptions = document.querySelectorAll(".sn-size-options button");
        if (!sizeOptions.length) return;

        sizeOptions.forEach(function (btn) {
            btn.addEventListener("click", function () {
                sizeOptions.forEach(function (b) { b.classList.remove("active"); });
                this.classList.add("active");

                var selectedSize = this.dataset.size || this.textContent.trim();

                /* BACKEND — Mise à jour prix/stock selon la taille */
                console.log("[product.js] Taille sélectionnée :", selectedSize);
            });
        });
    }


    // SÉLECTION COULEUR 
    function initColorSelection() {
        var colorDots = document.querySelectorAll(".sn-color-options .sn-color-dot");
        if (!colorDots.length) return;

        colorDots.forEach(function (dot) {
            dot.addEventListener("click", function () {
                colorDots.forEach(function (d) { d.classList.remove("active"); });
                this.classList.add("active");

                var selectedColor = this.dataset.color || this.title || "";
                var colorLabel    = document.querySelector(".sn-selected-color-label");
                if (colorLabel) colorLabel.textContent = selectedColor;

                /* BACKEND — Changer les images galerie selon couleur */
                console.log("[product.js] Couleur sélectionnée :", selectedColor);
            });
        });
    }


    // SÉLECTEUR DE QUANTITÉ
    function initQuantitySelector() {
        var qtyInput = document.querySelector(".sn-qty-input");
        var qtyBtns  = document.querySelectorAll(".sn-qty-btn");
        if (!qtyInput || !qtyBtns.length) return;

        qtyBtns.forEach(function (btn) {
            btn.addEventListener("click", function () {
                var current = parseInt(qtyInput.value, 10) || 1;
                var delta   = this.dataset.action === "increase" || this.textContent.trim() === "+"
                              ? 1 : -1;
                var min     = parseInt(qtyInput.min, 10) || 1;
                var max     = parseInt(qtyInput.max, 10) || 99;
                var next    = Math.min(max, Math.max(min, current + delta));

                qtyInput.value = next;
            });
        });

        // Validation saisie directe
        qtyInput.addEventListener("change", function () {
            var val = parseInt(this.value, 10);
            var min = parseInt(this.min, 10) || 1;
            var max = parseInt(this.max, 10) || 99;
            if (isNaN(val) || val < min) this.value = min;
            if (val > max) this.value = max;
        });
    }


    // AJOUTER AU PANIER depuis la fiche produit (EF-008)
    function initAddToCartProduct() {
        var addBtn = document.querySelector(".sn-add-to-cart-btn, .sn-btn-add-cart");
        if (!addBtn) return;

        addBtn.addEventListener("click", function (e) {
            e.preventDefault();

            // Vérifie qu'une taille est sélectionnée
            var sizeOptions   = document.querySelectorAll(".sn-size-options button");
            var selectedSize  = document.querySelector(".sn-size-options button.active");

            if (sizeOptions.length > 0 && !selectedSize) {

                var sizeSection = document.querySelector(".sn-size-options");
                if (sizeSection) {
                    sizeSection.classList.add("sn-error-shake");
                    setTimeout(function () {
                        sizeSection.classList.remove("sn-error-shake");
                    }, 600);
                }
                if (window.snShowToast) {
                    window.snShowToast("Veuillez sélectionner une taille.", "error");
                }
                return;
            }

            var productId  = addBtn.dataset.productId || "0";
            var qty        = parseInt(document.querySelector(".sn-qty-input") ?
                             document.querySelector(".sn-qty-input").value : "1", 10);
            var sizeVal    = selectedSize ? selectedSize.dataset.size || selectedSize.textContent.trim() : "";
            var colorVal   = (document.querySelector(".sn-color-dot.active") || {}).dataset
                             ? document.querySelector(".sn-color-dot.active").dataset.color : "";

            addToCartFromProduct(productId, qty, sizeVal, colorVal, addBtn);
        });
    }

    function addToCartFromProduct(productId, qty, size, color, btn) {
        var originalText = btn.textContent;
        btn.textContent  = "Adding...";
        btn.disabled     = true;

        /* BACKEND — Ajouter au panier Odoo (website_sale) */

        setTimeout(function () {
            btn.textContent = "✓ Added to Cart!";
            btn.classList.add("sn-btn--success");

            var badge = document.querySelector(".sn-cart-count");
            if (badge) {
                badge.textContent = (parseInt(badge.textContent, 10) || 0) + qty;
                badge.style.display = "flex";
            }

            if (window.snShowToast) window.snShowToast("Produit ajouté au panier !");

            setTimeout(function () {
                btn.textContent = originalText;
                btn.disabled    = false;
                btn.classList.remove("sn-btn--success");
            }, 2500);
        }, 700);
    }

    function initTabs() {
        var tabBtns   = document.querySelectorAll(".sn-tab-btn");
        var tabPanels = document.querySelectorAll(".sn-tab-panel");
        if (!tabBtns.length) return;

        tabBtns.forEach(function (btn) {
            btn.addEventListener("click", function () {
                var target = this.dataset.tab;

                tabBtns.forEach(function (b)   { b.classList.remove("active"); b.setAttribute("aria-selected", "false"); });
                tabPanels.forEach(function (p)  { p.classList.remove("active"); p.hidden = true; });

                this.classList.add("active");
                this.setAttribute("aria-selected", "true");

                var panel = document.getElementById("tab-" + target) ||
                            document.querySelector('[data-tab-panel="' + target + '"]');
                if (panel) {
                    panel.classList.add("active");
                    panel.hidden = false;
                }
            });
        });
    }


    function initWishlistToggle() {
        var wishBtn = document.querySelector(".sn-product-wishlist-btn, .sn-btn-wishlist");
        if (!wishBtn) return;

        var productId = wishBtn.dataset.productId || "0";

        var wishlist = getWishlist();
        if (wishlist.indexOf(productId) !== -1) {
            wishBtn.classList.add("sn-wishlist-btn--active");
        }

        wishBtn.addEventListener("click", function () {
            var wl       = getWishlist();
            var idx      = wl.indexOf(productId);
            var isActive = idx !== -1;

            if (isActive) {
                wl.splice(idx, 1);
                wishBtn.classList.remove("sn-wishlist-btn--active");
                if (window.snShowToast) window.snShowToast("Retiré de la wishlist");
            } else {
                wl.push(productId);
                wishBtn.classList.add("sn-wishlist-btn--active");
                if (window.snShowToast) window.snShowToast("Ajouté à la wishlist !");
            }

            saveWishlist(wl);

            /* BACKEND — Synchroniser la wishlist */
        });
    }

    function getWishlist() {
        try { return JSON.parse(localStorage.getItem("sn_wishlist") || "[]"); }
        catch (e) { return []; }
    }

    function saveWishlist(wl) {
        try { localStorage.setItem("sn_wishlist", JSON.stringify(wl)); }
        catch (e) { /* ignorer les erreurs de stockage */ }
    }

})();
