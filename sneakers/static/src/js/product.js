(function () {

    var productSection = document.querySelector(".sn-product-details");
    
    var currentVariantAvailable = true;

    var selectedSizeId = null;
    var selectedSize = null;

    var selectedColorId = null;
    var selectedColor = null;

    if (productSection) {

    initGallery();

    initSizeSelection();

    initColorSelection();

    initQuantitySelector();

    initAddToCartProduct();

    initTabs();

    initWishlistToggle();

}

function updateAddCartButton(button){

    if(!button){
        return;
    }


    var stock = parseInt(
        button.dataset.stock,
        10
    );


    var cartQty = parseFloat(
        button.dataset.cartQty
    ) || 0;



    if(!isNaN(stock) && cartQty >= stock){

        button.disabled = true;

        button.textContent =
            "Maximum quantity reached";

    }else{

        button.disabled = false;

        if(!button.textContent.includes("Backorder")){
            button.textContent = "Add to Cart";
        }

    }
}
function checkCartQuantityBeforeAdd(productId, stock, addQty){

return fetch('/shop/cart/get_product_quantity', {

    method:"POST",

    credentials:"include",

    headers:{
        "Content-Type":"application/json"
    },

    body:JSON.stringify({

        jsonrpc:"2.0",
        method:"call",

        params:{
            product_id:parseInt(productId)
        }

    })

})

.then(function(response){
    return response.json();
})

.then(function(data){

    var currentQty = 0;


    if(data.result){

        currentQty =
            parseFloat(data.result.quantity) || 0;

    }

    return (
        currentQty + addQty
    ) <= parseFloat(stock);

});

}


function getCartProductQuantity(productId){

    return fetch('/shop/cart/get_product_quantity', {

        method:"POST",

        credentials:"include",

        headers:{
            "Content-Type":"application/json"
        },

        body:JSON.stringify({

            jsonrpc:"2.0",
            method:"call",

            params:{
                product_id:parseInt(productId)
            }

        })

    })

    .then(function(response){
        return response.json();
    })

    .then(function(data){
        

        if(data.result){

            return parseFloat(data.result.quantity) || 0;

        }

        return 0;

    });

}
// Cards produit
initAddToCartCards();

function initAddToCartCards() {

    var buttons = document.querySelectorAll(
    ".sn-product-card:not(.sn-wishlist-item) .sn-add-cart"
);

    buttons.forEach(function(btn){

        var stock = parseInt(btn.dataset.stock,10);

        if(!isNaN(stock) && stock <= 0){

            btn.disabled = true;
            btn.textContent = "Out of stock";

        }

    });

    buttons.forEach(function(btn){

        btn.addEventListener("click", function(e){

    e.preventDefault();


    if(this.disabled){
        return;
    }


    if(!currentVariantAvailable){

                if(window.snShowToast){
                    window.snShowToast(
                        "Cette variante n'est pas disponible.",
                        "error"
                    );
                }

                return;
            }


            var productId = this.dataset.productId;
            var templateId = this.dataset.templateId;

            // Vérification stock depuis le bouton
            var stock = parseInt(this.dataset.stock, 10);


            if (isNaN(stock)) {

                stock = 999;

            }
            if(stock <= 0){

                if(window.snShowToast){

                    window.snShowToast(
                        "Produit hors stock",
                        "error"
                    );

                }

                return;
            }
            checkCartQuantityBeforeAdd(productId, stock,1)
.then(function(canAdd){


    if(!canAdd){

        btn.disabled = true;

        btn.textContent =
            "Maximum quantity reached";


        if(window.snShowToast){

            window.snShowToast(
                "Maximum quantity reached",
                "error"
            );

        }


        return;

    }
            fetch('/shop/cart/add', {

                method: "POST",
                credentials: "include",
                headers: {
                    "Content-Type": "application/json"
                },

                body: JSON.stringify({

                    jsonrpc: "2.0",
                    method: "call",

                    params: {
                        product_id: parseInt(productId),
                        product_template_id: parseInt(templateId),
                        add_qty: 1,
                        quantity: 1
                    }

                })

            })

            .then(function(response){
                return response.json();
            })

            .then(function(data){
                
                if (data.error) {

                    console.error(
                        "ODOO ERROR MESSAGE :",
                        data.error.message
                    );

                    console.error(
                        "ODOO ERROR DATA :",
                        data.error.data
                    );

                    console.error(
                        "ODOO DEBUG :",
                        data.error.data.debug
                    );

                    return;
                }
            // Vérification warning Odoo (stock insuffisant par exemple)
            if(data.result && data.result.warning){

                if(window.snShowToast){

                    window.snShowToast(
                        data.result.warning,
                        "error"
                    );

                }

                return;
            }


        if(data.result){

            var originalText = btn.textContent;

            btn.textContent = "✓ Added";

            btn.dataset.added = "true";


            setTimeout(function(){

                btn.dataset.added = "false";

                updateAddCartButton(btn);

            },10000);


            // Mise à jour quantité réelle panier
            getCartProductQuantity(productId)
            .then(function(productQty){

                btn.dataset.cartQty = productQty;

                updateAddCartButton(btn);

            });


            var badge = document.querySelector(".sn-cart-count");

            if(badge){

                badge.textContent = data.result.cart_quantity;
                badge.style.display = "flex";

            }


            setTimeout(function(){

                updateAddCartButton(btn);

            },10000);

            }

            })

            .catch(function(error){

                console.error(
                    "CARD ADD CART ERROR:",
                    error
                );

            });


        });

    });

    });

}
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

                selectedSizeId = Number(this.dataset.sizeId);

                selectedSize = this.dataset.size || this.textContent.trim();
                updateVariantStock();

            });
        });
    }


    // SÉLECTION COULEUR 
    function initColorSelection() {

    var colorDots = document.querySelectorAll(".sn-color-options .sn-color");

    if (!colorDots.length) return;


    colorDots.forEach(function (dot) {

        dot.addEventListener("click", function () {

            colorDots.forEach(function (d) {
                d.classList.remove("active");
            });


            this.classList.add("active");


            selectedColorId = Number(this.dataset.colorId);

            updateVariantStock();

            selectedColor = this.dataset.color || this.title || "";

            var colorLabel = document.querySelector(".sn-selected-color-label");

            if (colorLabel) {
                colorLabel.textContent = selectedColor;
            }


        });

    });

}


    // SÉLECTEUR DE QUANTITÉ
    function initQuantitySelector() {
        var qtyInput = document.querySelector(".sn-qty-input");
        var qtyBtns  = document.querySelectorAll(".sn-qty-btn");
        if (!qtyInput || !qtyBtns.length) return;
        if (qtyInput.getAttribute("data-stock") === null) {
    var maxStock = qtyInput.getAttribute("max");

    if (maxStock !== null) {
        qtyInput.setAttribute("data-stock", maxStock);
    }
}

        qtyBtns.forEach(function (btn) {

            btn.addEventListener("click", function () {

                var current = parseInt(qtyInput.value, 10) || 1;

                var delta = this.dataset.action === "increase" ||
                            this.textContent.trim() === "+"
                            ? 1
                            : -1;

                var min = parseInt(qtyInput.min, 10) || 1;

                var stock = qtyInput.getAttribute("data-stock");

                stock = stock !== null && stock !== ""
                    ? parseFloat(stock)
                    : null;

                var max = qtyInput.max
                    ? parseFloat(qtyInput.max)
                    : null;


                // Aucun stock disponible
                if (stock === 0) {

                    btn.disabled = true;

                    return;
                }


                var next = current + delta;


                if (max !== null) {
                    next = Math.min(max, next);
                }


                next = Math.max(min, next);


                qtyInput.value = next;

            });

        });

        // Validation saisie directe
        qtyInput.addEventListener("change", function () {
            var stock = parseInt(this.dataset.stock, 10);

            if (stock === 0) {
                this.value = 1;
                return;
            }

            var val = parseInt(this.value, 10);

            var min = parseInt(this.min, 10) || 1;

            var max = this.max
                ? parseInt(this.max, 10)
                : null;


            if (isNaN(val) || val < min) {
                this.value = min;
            }

            if (max !== null && val > max) {
                this.value = max;
            }

        });
    }


    // AJOUTER AU PANIER depuis la fiche produit (EF-008)
    function initAddToCartProduct() {

        var addBtn = productSection.querySelector(".sn-add-cart");


        if (!addBtn) {
            return;
        }

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

            var productId = addBtn.dataset.productId || "0";

            var templateId = addBtn.dataset.templateId || "0";


            var qty = parseInt(
                document.querySelector(".sn-qty-input")
                ? document.querySelector(".sn-qty-input").value
                : "1",
                10
            );


            if (!selectedSizeId && sizeOptions.length > 0) {

                return;

            }


            getVariantAndAddCart(
            templateId,
            qty,
            selectedSizeId,
            selectedColorId,
            addBtn
        );
        });
    }

    function updateVariantStock(){

    var addBtn = document.querySelector(".sn-add-cart");

    if(!addBtn){
        return;
    }

    var templateId = addBtn.dataset.templateId;


    var attributeIds = [];


    if(selectedColorId){
        attributeIds.push(parseInt(selectedColorId));
    }


    if(selectedSizeId){
        attributeIds.push(parseInt(selectedSizeId));
    }


    fetch('/get-product-variant', {

        method: 'POST',

        headers:{
            'Content-Type':'application/json'
        },

        body: JSON.stringify({

            jsonrpc:"2.0",

            method:"call",

            params:{
                template_id: templateId,
                attribute_value_ids: attributeIds
            }

        })

    })

    .then(function(response){
        return response.json();
    })

    .then(function(data){

    var qtyInput = document.querySelector(".sn-qty-input");


    // =========================
    // VARIANTE INEXISTANTE
    // =========================

    if(!data.result || !data.result.product_id){

        currentVariantAvailable = false;


        if(qtyInput){

            qtyInput.setAttribute("data-stock", 0);
            qtyInput.setAttribute("max", 0);
            qtyInput.value = 1;

        }


        addBtn.disabled = true;
        addBtn.textContent = "Variante indisponible";


        return;
    }



    // =========================
    // VARIANTE TROUVÉE
    // =========================

    currentVariantAvailable = true;


    if(!qtyInput){
        return;
    }



    var stock = data.result.qty_available;


    // Mettre à jour la variante actuelle
    addBtn.dataset.productId = data.result.product_id;

    addBtn.dataset.stock = stock;

    addBtn.dataset.cartQty = 0;

    qtyInput.setAttribute(
        "data-stock",
        stock
    );



    // =========================
    // STOCK DISPONIBLE
    // =========================

    if(stock > 0){

        currentVariantAvailable = true;

        addBtn.disabled = false;

        addBtn.textContent = "Add to Cart";
        


        qtyInput.setAttribute(
            "max",
            stock
        );


        var currentQty = parseInt(qtyInput.value,10) || 1;


        if(currentQty > stock){

            qtyInput.value = stock;

        }


    }


    // =========================
    // PAS DE STOCK
    // =========================

    else{


        currentVariantAvailable = false;


        addBtn.disabled = true;

        addBtn.textContent = "Out of stock";


        qtyInput.setAttribute(
            "max",
            0
        );


        qtyInput.value = 1;

    }


});

}

    function getVariantAndAddCart(templateId, qty, sizeId, colorId, btn) {
        var attributeIds = [];

        if (colorId) {
            attributeIds.push(parseInt(colorId));
        }

        if (sizeId) {
            attributeIds.push(parseInt(sizeId));
        }

        fetch('/get-product-variant', {

            method: 'POST',

            headers: {
                'Content-Type': 'application/json'
            },

            body: JSON.stringify({

                jsonrpc: "2.0",

                method: "call",

                params: {
                    template_id: templateId,
                    attribute_value_ids: attributeIds
                }

            })

        })

        .then(function(response){
            return response.json();
        })

        .then(function(data){

            if (!data.result || !data.result.product_id) {
                console.error("NO VARIANT FOUND", data);
                return;
            }


            if(data.result.qty_available !== undefined){

                if(data.result.qty_available <= 0){
                    console.error("Produit hors stock");
                    return;
                }

                qty = Math.min(
                    qty,
                    data.result.qty_available
                );

            }


            addToCartFromProduct(
                data.result.product_id,
                templateId,
                qty,
                btn,
                data.result.qty_available
            );

        });

    }

    function addToCartFromProduct(productId, templateId, qty, btn, stock) {

        btn.textContent = "Adding...";
        btn.disabled = true;


        fetch('/shop/cart/add', {

            method:'POST',
            credentials:"include",

            headers:{
                'Content-Type':'application/json'
            },

            body:JSON.stringify({

                jsonrpc:"2.0",

                method:"call",

                params:{
                    product_id:parseInt(productId),
                    product_template_id:parseInt(templateId),
                    add_qty:qty,
                    quantity:qty
                }

            })

        })

        .then(function(response){
            return response.json();
        })

        .then(function(data){


            if(data.error){

                console.error(
                    "ADD CART ERROR:",
                    data.error
                );

                return;

            }

            // Après ajout réel au panier
            var cartQty = 0;


    if(data.result && data.result.cart_quantity !== undefined){

        cartQty = data.result.cart_quantity;

    }


    getCartProductQuantity(productId)
    .then(function(productQty){

        btn.dataset.cartQty = productQty;

    });


    var badge = document.querySelector(".sn-cart-count");


    if(badge){

        badge.textContent = cartQty;
        badge.style.display = "flex";

    }

    btn.textContent = "✓ Added to Cart";

    btn.dataset.added = "true";


    setTimeout(function(){

        btn.dataset.added = "false";

        updateAddCartButton(btn);

    },10000);


        })

        .catch(function(error){

            console.error(
                "ADD CART FAILED:",
                error
            );

            btn.disabled = false;

            btn.textContent = "Add to Cart";

        });

    }

    function initTabs() {

        var tabBtns = document.querySelectorAll(".sn-tabs button");
        var tabPanels = document.querySelectorAll(".sn-tab-content");

        if (!tabBtns.length || !tabPanels.length) {
            return;
        }


        tabBtns.forEach(function (btn) {

            btn.addEventListener("click", function () {

            var target = this.dataset.tab;


            // Désactiver tous les boutons
            tabBtns.forEach(function (b) {
                b.classList.remove("active");
            });


            // Cacher tous les contenus
            tabPanels.forEach(function (panel) {
                panel.style.display = "none";
            });


            // Activer le bouton cliqué
            this.classList.add("active");


            // Afficher le contenu correspondant
            var panel = document.getElementById(target);

            if (panel) {
                panel.style.display = "block";
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

/* ============================================================
   CART PAGE — +/− QUANTITY BUTTONS (/shop/cart)
   ============================================================ */
(function initCartQtyButtons() {
    var cartContainer = document.querySelector('.js_cart_lines, .o_cart_product');
    if (!cartContainer) return;

    document.querySelectorAll('.o_cart_product').forEach(function(row) {
        var qtyInput = row.querySelector('.js_quantity');
        if (!qtyInput || qtyInput.dataset.qtyBtn) return;
        qtyInput.dataset.qtyBtn = '1';

        var wrapper = qtyInput.closest('.css_quantity') || qtyInput.parentElement;

        /* Remove readonly so buttons work */
        qtyInput.removeAttribute('readonly');

        /* Create minus button */
        var minusBtn = document.createElement('button');
        minusBtn.type = 'button';
        minusBtn.className = 'sn-qty-btn sn-qty-minus';
        minusBtn.textContent = '−';
        minusBtn.addEventListener('click', function() {
            var val = parseInt(qtyInput.value, 10);
            if (val > 1) {
                qtyInput.value = val - 1;
                qtyInput.dispatchEvent(new Event('change', {bubbles: true}));
            }
        });

        /* Create plus button */
        var plusBtn = document.createElement('button');
        plusBtn.type = 'button';
        plusBtn.className = 'sn-qty-btn sn-qty-plus';
        plusBtn.textContent = '+';
        plusBtn.addEventListener('click', function() {
            var val = parseInt(qtyInput.value, 10);
            qtyInput.value = val + 1;
            qtyInput.dispatchEvent(new Event('change', {bubbles: true}));
        });

        /* Insert buttons */
        wrapper.insertBefore(minusBtn, qtyInput);
        wrapper.appendChild(plusBtn);
    });
})();