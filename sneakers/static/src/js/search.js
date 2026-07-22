document.addEventListener("DOMContentLoaded", function () {

    var searchForm  = document.querySelector(".sn-search");
    if (!searchForm) return;

    var searchInput = searchForm.querySelector('input[type="search"]');
    if (!searchInput) return;

    var dropdown = document.createElement("div");
    dropdown.className = "sn-autocomplete";
    dropdown.setAttribute("role", "listbox");
    dropdown.setAttribute("aria-label", "Suggestions de recherche");
    dropdown.style.display = "none";
    searchForm.style.position = "relative";
    searchForm.appendChild(dropdown);

    var MIN_CHARS   = 3;      
    var DEBOUNCE_MS = 300;    
    var debounceTimer = null;
    var currentQuery  = "";

    // Ces données doivent être remplacées par l'appel API réel ci-dessous.
    var DEMO_PRODUCTS = [
        { type: "product", label: "Nike Air Max 270",   url: "/product?id=1",  badge: "$189" },
        { type: "product", label: "Nike Air Force 1",   url: "/product?id=2",  badge: "$120" },
        { type: "product", label: "Adidas Ultraboost",  url: "/product?id=3",  badge: "$175" },
        { type: "product", label: "Adidas Stan Smith",  url: "/product?id=4",  badge: "$95"  },
        { type: "product", label: "Puma RS-X",          url: "/product?id=5",  badge: "$160" },
        { type: "product", label: "New Balance 574",    url: "/product?id=6",  badge: "$130" },
        { type: "product", label: "Converse All Star",  url: "/product?id=7",  badge: "$85"  },
        { type: "product", label: "Vans Old Skool",     url: "/product?id=8",  badge: "$75"  },
        { type: "product", label: "Reebok Classic",     url: "/product?id=9",  badge: "$110" },
        { type: "product", label: "Jordan 1 Retro",     url: "/product?id=10", badge: "$220" },
    ];

    var DEMO_CATEGORIES = [
        { type: "category", label: "Running",      url: "/shop-sneakers?category=running"    },
        { type: "category", label: "Basketball",   url: "/shop-sneakers?category=basketball" },
        { type: "category", label: "Lifestyle",    url: "/shop-sneakers?category=lifestyle"  },
        { type: "category", label: "Hommes",       url: "/shop-sneakers?category=men"        },
        { type: "category", label: "Femmes",       url: "/shop-sneakers?category=women"      },
        { type: "category", label: "Soldes",       url: "/shop-sneakers?category=sale"       },
    ];

    // ─── Fonction de recherche ────────────────────────────────────────
    function fetchSuggestions(query) {
        currentQuery = query;

        /* Remplacer le bloc "démo" ci-dessous par un appel réel */

        // Mode démo : filtrage local
        var q = query.toLowerCase();

        var matchedProducts   = DEMO_PRODUCTS.filter(function (p) {
            return p.label.toLowerCase().indexOf(q) !== -1;
        }).slice(0, 5);

        var matchedCategories = DEMO_CATEGORIES.filter(function (c) {
            return c.label.toLowerCase().indexOf(q) !== -1;
        }).slice(0, 3);

        renderSuggestions(matchedCategories.concat(matchedProducts), query);
    }

    // Affichage des suggestions
    function renderSuggestions(results, query) {
        dropdown.innerHTML = "";

        if (!results.length) {
            dropdown.style.display = "none";
            return;
        }

        var categories = results.filter(function (r) { return r.type === "category"; });
        var products   = results.filter(function (r) { return r.type === "product";  });

        function highlight(text, q) {
            var re  = new RegExp("(" + escapeRegex(q) + ")", "gi");
            return text.replace(re, "<mark>$1</mark>");
        }

        function buildSection(title, items, iconClass) {
            if (!items.length) return;

            var header = document.createElement("div");
            header.className   = "sn-autocomplete-group";
            header.textContent = title;
            dropdown.appendChild(header);

            items.forEach(function (item) {
                var el = document.createElement("a");
                el.className = "sn-autocomplete-item sn-autocomplete-item--" + item.type;
                el.href      = item.url;
                el.setAttribute("role", "option");

                var icon = document.createElement("i");
                icon.className = iconClass;
                el.appendChild(icon);

                var labelSpan = document.createElement("span");
                labelSpan.className   = "sn-autocomplete-label";
                labelSpan.innerHTML   = highlight(item.label, query);
                el.appendChild(labelSpan);

                if (item.badge) {
                    var badge = document.createElement("span");
                    badge.className   = "sn-autocomplete-badge";
                    badge.textContent = item.badge;
                    el.appendChild(badge);
                }

                dropdown.appendChild(el);
            });
        }

        buildSection("Catégories", categories, "fa fa-tag");
        buildSection("Produits",   products,   "fa fa-shoe-prints");

        // Lien « Voir tous les résultats »
        var seeAll = document.createElement("a");
        seeAll.className = "sn-autocomplete-see-all";
        seeAll.href      = "/shop-sneakers?search=" + encodeURIComponent(query);
        seeAll.innerHTML = 'Voir tous les résultats pour <strong>"' + query + '"</strong>';
        dropdown.appendChild(seeAll);

        dropdown.style.display = "block";
    }

    function closeDropdown() {
        dropdown.style.display = "none";
        dropdown.innerHTML     = "";
    }

    function escapeRegex(str) {
        return str.replace(/[.*+?^${}()|[\]\\]/g, "\\$&");
    }

    // Événements input
    searchInput.addEventListener("input", function () {
        var val = this.value.trim();

        clearTimeout(debounceTimer);

        if (val.length < MIN_CHARS) {
            closeDropdown();
            return;
        }

        debounceTimer = setTimeout(function () {
            fetchSuggestions(val);
        }, DEBOUNCE_MS);
    });

    // Navigation clavier dans les suggestions
    searchInput.addEventListener("keydown", function (e) {
        var items = dropdown.querySelectorAll(".sn-autocomplete-item");
        var focused = dropdown.querySelector(".sn-autocomplete-item--focused");
        var idx = -1;

        if (e.key === "Escape") {
            closeDropdown();
            return;
        }

        if (!items.length) return;

        items.forEach(function (item, i) {
            if (item === focused) idx = i;
        });

        if (e.key === "ArrowDown") {
            e.preventDefault();
            var next = items[idx + 1] || items[0];
            if (focused) focused.classList.remove("sn-autocomplete-item--focused");
            next.classList.add("sn-autocomplete-item--focused");
            searchInput.value = next.querySelector(".sn-autocomplete-label").textContent;
        }

        if (e.key === "ArrowUp") {
            e.preventDefault();
            var prev = items[idx - 1] || items[items.length - 1];
            if (focused) focused.classList.remove("sn-autocomplete-item--focused");
            prev.classList.add("sn-autocomplete-item--focused");
            searchInput.value = prev.querySelector(".sn-autocomplete-label").textContent;
        }

        if (e.key === "Enter" && focused) {
            e.preventDefault();
            window.location.href = focused.href;
        }
    });

    // Fermer si clic ailleurs
    document.addEventListener("click", function (e) {
        if (!searchForm.contains(e.target)) {
            closeDropdown();
        }
    });

    // Fermer à la soumission du formulaire
    searchForm.addEventListener("submit", function () {
        closeDropdown();
    });

});
