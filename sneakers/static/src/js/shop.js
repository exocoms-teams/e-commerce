(function () {

    var shopSection = document.querySelector(".sn-shop");
    if (!shopSection) return;

    var activeFilters = {
        brands:       [],  // ex: ["Nike", "Adidas"]
        sizes:        [],  // ex: ["42", "43"]
        colors:       [],  // ex: ["Black", "White"]
        priceMin:     0,
        priceMax:     9999,
        availability: false,
        sortBy:       "default",
        page:         1,
        perPage:      12
    };

    // Éléments DOM 
    var brandCheckboxes  = document.querySelectorAll('.sn-filter-box .sn-checkbox input[type="checkbox"]');
    var sizeButtons      = document.querySelectorAll(".sn-size-list button");
    var colorSwatches    = document.querySelectorAll(".sn-color-swatch");
    var priceMinInput    = document.querySelector(".sn-price-min");
    var priceMaxInput    = document.querySelector(".sn-price-max");
    var priceRangeSlider = document.querySelector(".sn-price-slider");
    var availToggles     = document.querySelectorAll(".sn-availability-toggle");
    var sortSelect       = document.querySelector(".sn-sort-select");
    var clearFiltersBtn  = document.querySelector(".sn-clear-filters");
    var activeFiltersBar = document.querySelector(".sn-active-filters");
    var productGrid      = document.querySelector(".sn-product-grid");
    var paginationNav    = document.querySelector(".sn-pagination");

    // ================================================
    // RESTAURER LES BRANDS DEPUIS L'URL
    // ================================================

    var urlParams = new URLSearchParams(window.location.search);

    urlParams.getAll("brand").forEach(function(id){

        var checkbox = document.querySelector(
            '.sn-filter-box .sn-checkbox input[value="' + id + '"]'
        );

        if(checkbox){

            checkbox.checked = true;

            activeFilters.brands.push({
                id: id,
                name: checkbox.dataset.brandName
            });

        }

    });

    function loadFiltersFromURL() {

        var params = new URLSearchParams(window.location.search);


        // BRANDS
        activeFilters.brands = [];

        params.getAll("brand").forEach(function(id){

            var checkbox = document.querySelector(
                '.sn-checkbox input[value="' + id + '"]'
            );

            if(checkbox){

                checkbox.checked = true;

                activeFilters.brands.push({
                    id: id,
                    name: checkbox.dataset.brandName
                });

            }

        });



        // SIZES
        activeFilters.sizes = [];

        params.getAll("size").forEach(function(sizeId){

            activeFilters.sizes.push(sizeId);

            var btn = document.querySelector(
                '.sn-size-btn[data-size="' + sizeId + '"]'
            );

            if(btn){
                btn.classList.add("active");
            }

        });



        // COLORS
        activeFilters.colors = [];

        params.getAll("color").forEach(function(colorId){

            activeFilters.colors.push(colorId);

            var swatch = document.querySelector(
                '.sn-color-swatch[data-color-id="' + colorId + '"]'
            );

            if(swatch){
                swatch.classList.add("active");
            }

        });



        // PRICE

        activeFilters.priceMin =
            parseInt(
                params.get("price_min") || 0
            );


        activeFilters.priceMax =
            parseInt(
                params.get("price_max") || 500
            );



        if(priceMinInput){
            priceMinInput.value = activeFilters.priceMin;
        }


        if(priceMaxInput){
            priceMaxInput.value = activeFilters.priceMax;
        }



        // AVAILABILITY

        activeFilters.availability =
            params.get("availability") || false;


        if(activeFilters.availability){

            var radio = document.querySelector(
                '.sn-availability-toggle[value="' +
                activeFilters.availability +
                '"]'
            );


            if(radio){
                radio.checked = true;
            }

        }

        // SORT

        activeFilters.sortBy =
            params.get("sort") || "popular";


        if(sortSelect){

            sortSelect.value = activeFilters.sortBy;

        }

    }

    // FILTRES MARQUE (checkboxes) 
    brandCheckboxes.forEach(function (checkbox) {

        checkbox.addEventListener("change", function () {

            var brandId = this.value;
            var brandName = this.dataset.brandName;


            if (this.checked) {

                activeFilters.brands.push({
                    id: brandId,
                    name: brandName
                });


            } else {

                activeFilters.brands =
                    activeFilters.brands.filter(function (brand) {

                        return brand.id !== brandId;

                    });

            }


            activeFilters.page = 1;

            applyFilters();

        });

    });

    //  FILTRES TAILLE
    sizeButtons.forEach(function (btn) {
        btn.addEventListener("click", function () {
            var size = this.dataset.size;
            this.classList.toggle("active");

            if (this.classList.contains("active")) {
                if (activeFilters.sizes.indexOf(size) === -1) {
                    activeFilters.sizes.push(size);
                }
            } else {
                activeFilters.sizes = activeFilters.sizes.filter(function (s) {
                    return s !== size;
                });
            }

            activeFilters.page = 1;
            applyFilters();
        });
    });

    // FILTRES COULEUR 
    colorSwatches.forEach(function (swatch) {

        swatch.addEventListener("click", function () {

            var colorId = this.dataset.colorId;

            this.classList.toggle("active");

            if(this.classList.contains("active")){

                if(activeFilters.colors.indexOf(colorId) === -1){
                    activeFilters.colors.push(colorId);
                }

            }else{

                activeFilters.colors =
                activeFilters.colors.filter(function(c){
                    return c !== colorId;
                });

            }

            activeFilters.page = 1;
            applyFilters();

        });

    });

    // FILTRE PRIX 
    if (priceMinInput) {
        priceMinInput.addEventListener("input", function () {
            var val = parseInt(this.value, 10);
            if (val >= activeFilters.priceMax) {
                this.value = activeFilters.priceMax - 10;
                return;
            }
            activeFilters.priceMin = val;
            updatePriceDisplay();
            debounceApply();
        });
    }

    if (priceMaxInput) {
        priceMaxInput.addEventListener("input", function () {
            var val = parseInt(this.value, 10);
            if (val <= activeFilters.priceMin) {
                this.value = activeFilters.priceMin + 10;
                return;
            }
            activeFilters.priceMax = val;
            updatePriceDisplay();
            debounceApply();
        });
    }

    if (priceRangeSlider) {
        priceRangeSlider.addEventListener("input", function () {
            activeFilters.priceMax = parseInt(this.value, 10);
            updatePriceDisplay();
            debounceApply();
        });
    }

    function updatePriceDisplay() {
        var minLabel = document.querySelector(".sn-price-label-min");
        var maxLabel = document.querySelector(".sn-price-label-max");
        if (minLabel) minLabel.textContent = "$" + activeFilters.priceMin;
        if (maxLabel) maxLabel.textContent = "$" + activeFilters.priceMax;

        if (priceRangeSlider) {
            var pct = (activeFilters.priceMin / parseInt(priceRangeSlider.max, 10)) * 100;
            priceRangeSlider.style.setProperty('--min-pct', pct + '%');
        }
    }

    // FILTRE DISPONIBILITÉ 
    if (availToggles.length) {

        availToggles.forEach(function(toggle){

            toggle.addEventListener("change", function(){

                activeFilters.availability = this.value;

                activeFilters.page = 1;

                applyFilters();

            });

        });

    }

    // TRI 
    if (sortSelect) {
        sortSelect.addEventListener("change", function () {
            activeFilters.sortBy = this.value;
            activeFilters.page   = 1;
            applyFilters();
        });
    }

    // EFFACER TOUS LES FILTRES
    if (clearFiltersBtn) {
        clearFiltersBtn.addEventListener("click", function () {
            resetAllFilters();
        });
    }

    function resetAllFilters() {
        activeFilters.brands       = [];
        activeFilters.sizes        = [];
        activeFilters.colors       = [];
        activeFilters.priceMin     = 0;
        activeFilters.priceMax     = 9999;
        activeFilters.availability = false;
        activeFilters.sortBy       = "default";
        activeFilters.page         = 1;

        // Reset UI
        brandCheckboxes.forEach(function (cb) { cb.checked = false; });
        sizeButtons.forEach(function (btn)     { btn.classList.remove("active"); });
        colorSwatches.forEach(function (sw)    { sw.classList.remove("active"); });
        availToggles.forEach(function(r){
            r.checked = false;
        });
        if (sortSelect)  sortSelect.value    = "default";
        if (priceRangeSlider) priceRangeSlider.value = priceRangeSlider.max;

        updatePriceDisplay();

        // Clear ALL URL params (including server-side ones like category)
        window.location.href = "/shop-sneakers";
    }

    // APPLIQUER LES FILTRES
    function applyFilters() {
        updateActiveFiltersBar();
        fetchProducts();
    }

    var debounceTimer = null;
    function debounceApply() {
        clearTimeout(debounceTimer);
        debounceTimer = setTimeout(function () {
            activeFilters.page = 1;
            applyFilters();
        }, 400);
    }

    // BARRE DE FILTRES ACTIFS 
    function updateActiveFiltersBar() {
        if (!activeFiltersBar) return;

        // Supprimer les tags existants (garde le bouton "Clear All")
        var existingTags = activeFiltersBar.querySelectorAll(".sn-filter-tag");
        existingTags.forEach(function (tag) { tag.remove(); });

        var hasFilters = false;

        function addTag(label, removeCallback) {
            hasFilters = true;
            var tag = document.createElement("span");
            tag.className   = "sn-filter-tag";
            tag.innerHTML   = label + ' <button aria-label="Supprimer ce filtre">×</button>';
            tag.querySelector("button").addEventListener("click", removeCallback);
            activeFiltersBar.insertBefore(tag, clearFiltersBtn);
        }

        activeFilters.brands.forEach(function (brand) {

            addTag(brand.name, function () {


                activeFilters.brands =
                    activeFilters.brands.filter(function (b) {

                        return b.id !== brand.id;

                    });


                brandCheckboxes.forEach(function(cb){

                    if(cb.value === brand.id){
                        cb.checked = false;
                    }

                });


                applyFilters();

            });

        });

        activeFilters.sizes.forEach(function (size) {
            addTag("Taille " + size, function () {
                activeFilters.sizes = activeFilters.sizes.filter(function (s) { return s !== size; });
                sizeButtons.forEach(function (btn) {
                    if (btn.textContent.trim() === size) btn.classList.remove("active");
                });
                applyFilters();
            });
        });

        activeFilters.colors.forEach(function (colorId) {

            var swatch = document.querySelector(
                '.sn-color-swatch[data-color-id="' + colorId + '"]'
            );

            var colorName = swatch ? swatch.title : colorId;


            addTag(colorName, function () {
                activeFilters.colors = activeFilters.colors.filter(function (c) { return c !== color; });
                colorSwatches.forEach(function (sw) {
                    if ((sw.dataset.color || sw.title) === color) sw.classList.remove("active");
                });
                applyFilters();
            });
        });

        if (activeFilters.priceMax < 9999) {
            addTag("Prix ≤ $" + activeFilters.priceMax, function () {
                activeFilters.priceMax = 9999;
                if (priceRangeSlider) priceRangeSlider.value = priceRangeSlider.max;
                updatePriceDisplay();
                applyFilters();
            });
        }

        if(activeFilters.availability){

            var label =
                activeFilters.availability === "in_stock"
                ? "In Stock"
                : "Out of Stock";


            addTag(label,function(){

                activeFilters.availability=false;

                availToggles.forEach(function(r){
                    r.checked=false;
                });

                applyFilters();

            });

        }

        if (clearFiltersBtn) {
            clearFiltersBtn.style.display = hasFilters ? "inline-flex" : "none";
        }
    }

    // 10. APPEL PRODUITS (avec filtres)
    function fetchProducts() {

        var params = new URLSearchParams(window.location.search);


        // =====================
        // BRANDS
        // =====================

        params.delete("brand");

        activeFilters.brands.forEach(function(brand){

            params.append(
                "brand",
                brand.id
            );

        });


        // =====================
        // SIZES
        // =====================

        params.delete("size");

        activeFilters.sizes.forEach(function(size){

            params.append(
                "size",
                size
            );

        });



        // =====================
        // COLORS
        // =====================

        params.delete("color");

        activeFilters.colors.forEach(function(color){

            params.append(
                "color",
                color
            );

        });



        // =====================
        // PRICE
        // =====================

        if (activeFilters.priceMin > 0) {
            params.set("price_min", activeFilters.priceMin);
        } else {
            params.delete("price_min");
        }

        if (activeFilters.priceMax < 9999) {
            params.set("price_max", activeFilters.priceMax);
        } else {
            params.delete("price_max");
        }

        // =====================
        // AVAILABILITY
        // =====================

        if (activeFilters.availability) {
            params.set("availability", activeFilters.availability);
        } else {
            params.delete("availability");
        }

        // PAGE
        if (activeFilters.page > 1) {
            params.set("page", activeFilters.page);
        } else {
            params.delete("page");
        }

        // SORT — only set if not default
        if (activeFilters.sortBy && activeFilters.sortBy !== "default") {
            params.set("sort", activeFilters.sortBy);
        } else {
            params.delete("sort");
        }

        window.location.href =
            "/shop-sneakers?" + params.toString();

    }

    // PAGINATION
    function updatePaginationUI(currentPage, totalPages) {
        if (!paginationNav) return;

        var buttons = paginationNav.querySelectorAll(".sn-page-btn:not(.sn-page-prev):not(.sn-page-next)");
        buttons.forEach(function (btn) {
            btn.classList.toggle("active", parseInt(btn.textContent, 10) === currentPage);
        });
    }

    

    // Délégation clic pagination
    if (paginationNav) {
        paginationNav.addEventListener("click", function (e) {
            var btn = e.target.closest(".sn-page-btn");
            if (!btn) return;

            var text = btn.textContent.trim();
            var icon = btn.querySelector("i");

            if (icon && icon.classList.contains("fa-chevron-left")) {
                activeFilters.page = Math.max(1, activeFilters.page - 1);
            } else if (icon && icon.classList.contains("fa-chevron-right")) {
                activeFilters.page = activeFilters.page + 1;
            } else {
                var page = parseInt(text, 10);
                if (!isNaN(page)) activeFilters.page = page;
            }

            applyFilters();
            if (productGrid) {
                productGrid.scrollIntoView({ behavior: "smooth", block: "start" });
            }
        });
    }

     
    // Délégation clic pagination
    if (paginationNav) {

        // Récupérer le nombre total de pages depuis le dernier bouton numéroté
        function getTotalPages() {
            var numbered = Array.from(paginationNav.querySelectorAll(".sn-page-btn")).filter(function(b) {
                return !b.querySelector("i") && !isNaN(parseInt(b.textContent.trim(), 10));
            });
            if (!numbered.length) return 1;
            return parseInt(numbered[numbered.length - 1].textContent.trim(), 10);
        }

        // Mettre à jour l'état visuel des flèches et du bouton actif
        function updatePaginationUI(currentPage) {
            var totalPages = getTotalPages();

            var prevBtn = paginationNav.querySelector(".sn-page-btn .fa-chevron-left");
            var nextBtn = paginationNav.querySelector(".sn-page-btn .fa-chevron-right");

            if (prevBtn) {
                prevBtn.closest(".sn-page-btn").style.visibility = currentPage <= 1 ? "hidden" : "visible";
            }
            if (nextBtn) {
                nextBtn.closest(".sn-page-btn").style.visibility = currentPage >= totalPages ? "hidden" : "visible";
            }

            // Un seul bouton actif à la fois
            paginationNav.querySelectorAll(".sn-page-btn").forEach(function(b) {
                b.classList.remove("active");
            });

            // Activer le bouton correspondant à la page actuelle
            paginationNav.querySelectorAll(".sn-page-btn").forEach(function(b) {
                if (!b.querySelector("i") && parseInt(b.textContent.trim(), 10) === currentPage) {
                    b.classList.add("active");
                }
            });
        }

        // Initialiser l'UI au chargement depuis l'URL
        var initialPage = parseInt(new URLSearchParams(window.location.search).get("page") || "1", 10);
        activeFilters.page = initialPage;
        updatePaginationUI(initialPage);


        paginationNav.addEventListener("click", function (e) {
            var btn = e.target.closest(".sn-page-btn");
            if (!btn) return;

            // Ignorer les flèches cachées
            if (btn.style.visibility === "hidden") return;

            var icon = btn.querySelector("i");
            var text = btn.textContent.trim();
            var totalPages = getTotalPages();

            // Source de vérité : lire la page courante DEPUIS L'URL, pas depuis activeFilters
            var currentPage = parseInt(new URLSearchParams(window.location.search).get("page") || "1", 10);
            var targetPage;

            if (icon && icon.classList.contains("fa-chevron-left")) {
                if (currentPage <= 1) return;
                targetPage = currentPage - 1;
            } else if (icon && icon.classList.contains("fa-chevron-right")) {
                if (currentPage >= totalPages) return;
                targetPage = currentPage + 1;
            } else {
                targetPage = parseInt(text, 10);
                if (isNaN(targetPage)) return;
            }

            activeFilters.page = targetPage;
            updatePaginationUI(targetPage);

            var url = new URL(window.location.href);
            url.searchParams.set("page", targetPage);
            window.location.href = url.toString();

            if (productGrid) {
                productGrid.scrollIntoView({ behavior: "smooth", block: "start" });
            }
        });
    }

    // FILTRE MOBILE
    var filterToggleBtn = document.querySelector(".sn-filter-toggle");
    var sidebar         = document.querySelector(".sn-shop-sidebar");

    if (filterToggleBtn && sidebar) {
        filterToggleBtn.addEventListener("click", function () {
            sidebar.classList.toggle("sn-shop-sidebar--open");
            this.setAttribute(
                "aria-expanded",
                sidebar.classList.contains("sn-shop-sidebar--open") ? "true" : "false"
            );
        });

        // Overlay de fermeture (mobile)
        var overlay = document.createElement("div");
        overlay.className = "sn-sidebar-overlay";
        document.body.appendChild(overlay);

        overlay.addEventListener("click", function () {
            sidebar.classList.remove("sn-shop-sidebar--open");
            filterToggleBtn.setAttribute("aria-expanded", "false");
        });

        sidebar.addEventListener("click", function (e) {
            if (sidebar.classList.contains("sn-shop-sidebar--open")) {
                overlay.style.display = "";
            } else {
                overlay.style.display = "none";
            }
        });
    }

    // Initialisation
    
    loadFiltersFromURL();

    updateActiveFiltersBar();

    // Lire le paramètre page depuis l'URL au chargement
    var urlPage = parseInt(new URLSearchParams(window.location.search).get("page") || "1", 10);
    activeFilters.page = urlPage;
    // Marquer le bon bouton comme actif
    paginationNav && paginationNav.querySelectorAll(".sn-page-btn").forEach(function(btn) {
        if (parseInt(btn.textContent, 10) === urlPage) btn.classList.add("active");
    });
    
    updatePriceDisplay();

})();
