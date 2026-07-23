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
    var availToggle      = document.querySelector(".sn-availability-toggle");
    var sortSelect       = document.querySelector(".sn-sort-select");
    var clearFiltersBtn  = document.querySelector(".sn-clear-filters");
    var activeFiltersBar = document.querySelector(".sn-active-filters");
    var productGrid      = document.querySelector(".sn-product-grid");
    var paginationNav    = document.querySelector(".sn-pagination");

    // FILTRES MARQUE (checkboxes) 
    brandCheckboxes.forEach(function (checkbox) {
        checkbox.addEventListener("change", function () {
            var brand = this.closest(".sn-checkbox").textContent.trim();

            if (this.checked) {
                if (activeFilters.brands.indexOf(brand) === -1) {
                    activeFilters.brands.push(brand);
                }
            } else {
                activeFilters.brands = activeFilters.brands.filter(function (b) {
                    return b !== brand;
                });
            }

            activeFilters.page = 1;
            applyFilters();
        });
    });

    //  FILTRES TAILLE
    sizeButtons.forEach(function (btn) {
        btn.addEventListener("click", function () {
            var size = this.textContent.trim();
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
            var color = this.dataset.color || this.title || this.getAttribute("aria-label") || "";
            this.classList.toggle("active");

            if (this.classList.contains("active")) {
                if (activeFilters.colors.indexOf(color) === -1) {
                    activeFilters.colors.push(color);
                }
            } else {
                activeFilters.colors = activeFilters.colors.filter(function (c) {
                    return c !== color;
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
    }

    // FILTRE DISPONIBILITÉ 
    if (availToggle) {
        availToggle.addEventListener("change", function () {
            activeFilters.availability = this.checked;
            activeFilters.page         = 1;
            applyFilters();
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
        if (availToggle) availToggle.checked = false;
        if (sortSelect)  sortSelect.value    = "default";
        if (priceRangeSlider) priceRangeSlider.value = priceRangeSlider.max;

        updatePriceDisplay();
        applyFilters();
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
            addTag(brand, function () {
                activeFilters.brands = activeFilters.brands.filter(function (b) { return b !== brand; });
                // Décocher la checkbox correspondante
                brandCheckboxes.forEach(function (cb) {
                    if (cb.closest(".sn-checkbox").textContent.trim() === brand) {
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

        activeFilters.colors.forEach(function (color) {
            addTag(color, function () {
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

        if (activeFilters.availability) {
            addTag("En stock", function () {
                activeFilters.availability = false;
                if (availToggle) availToggle.checked = false;
                applyFilters();
            });
        }

        if (clearFiltersBtn) {
            clearFiltersBtn.style.display = hasFilters ? "inline-flex" : "none";
        }
    }

    // 10. APPEL PRODUITS (avec filtres)
    function fetchProducts() {
        if (productGrid) {
            productGrid.classList.add("sn-product-grid--loading");
        }

        /* BACKEND — Récupérer les produits filtrés*/

        // Simulation frontend
        setTimeout(function () {
            if (productGrid) productGrid.classList.remove("sn-product-grid--loading");
            updatePaginationUI(1, 3); // page 1 sur 3 (démo)
        }, 500);
    }

    // PAGINATION
    function updatePaginationUI(currentPage, totalPages) {
        if (!paginationNav) return;

        var buttons = paginationNav.querySelectorAll(".sn-page-btn:not(.sn-page-prev):not(.sn-page-next)");
        buttons.forEach(function (btn) {
            btn.classList.toggle("active", parseInt(btn.textContent, 10) === currentPage);
        });
    }

    const paginationNav = document.querySelector(".sn-pagination");
    const productGrid = document.querySelector(".sn-products-grid");

    function updatePaginationArrows() {

        const prevBtn = paginationNav.querySelector(".sn-prev-btn");
        const nextBtn = paginationNav.querySelector(".sn-next-btn");
        const lastPage = paginationNav.querySelectorAll(".sn-page-btn[data-page]").length;

        if (activeFilters.page === 1) {
            prevBtn.style.visibility = "hidden";
        } else {
            prevBtn.style.visibility = "visible";
        }

        if (activeFilters.page === lastPage) {
            nextBtn.style.visibility = "hidden";
        } else {
            nextBtn.style.visibility = "visible";
        }

    }

    // Délégation clic pagination
    if (paginationNav) {

        paginationNav.addEventListener("click", function (e) {

            const btn = e.target.closest(".sn-page-btn");
            if (!btn) return;

            const icon = btn.querySelector("i");
            const lastPage = paginationNav.querySelectorAll(".sn-page-btn[data-page]").length;

            // Calcul de la nouvelle page
            if (icon && icon.classList.contains("fa-chevron-left")) {

                activeFilters.page = Math.max(1, activeFilters.page - 1);

            } else if (icon && icon.classList.contains("fa-chevron-right")) {

                activeFilters.page = Math.min(lastPage, activeFilters.page + 1);

            } else {

                const page = parseInt(btn.dataset.page, 10);

                if (!isNaN(page)) {
                    activeFilters.page = page;
                }

            }

            // Mise à jour du bouton actif
            paginationNav.querySelectorAll(".sn-page-btn").forEach(function (b) {
                b.classList.remove("active");
            });

            const activeBtn = paginationNav.querySelector(
                `.sn-page-btn[data-page="${activeFilters.page}"]`
            );

            if (activeBtn) {
                activeBtn.classList.add("active");
            }

            // Redirection (temporairement vers la même page)
            const url = new URL(window.location.href);
            url.searchParams.set("page", activeFilters.page);
            window.location.href = url.toString();

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
    updateActiveFiltersBar();

    // Lire le paramètre page depuis l'URL au chargement
    var urlPage = parseInt(new URLSearchParams(window.location.search).get("page") || "1", 10);
    activeFilters.page = urlPage;
    // Marquer le bon bouton comme actif
    paginationNav && paginationNav.querySelectorAll(".sn-page-btn").forEach(function(btn) {
        if (parseInt(btn.textContent, 10) === urlPage) btn.classList.add("active");
});

})();
