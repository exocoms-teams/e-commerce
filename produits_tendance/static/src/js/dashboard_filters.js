/**
 * produits_tendance — Filtres dynamiques du dashboard (WIN-45 / WIN-50)
 *
 * Écoute les changements des selects du panneau de filtres
 * (.o_winners_filter_panel), appelle /api/dashboard/filter en AJAX
 * (GET, JSON) et reconstruit uniquement la grille de cartes produit
 * (#o_winners_product_grid), sans recharger la page.
 *
 * Reproduit côté client le même balisage que le sous-template QWeb
 * produits_tendance.template_product_cards, pour que le rendu initial
 * (serveur) et le rendu filtré (client) restent visuellement identiques.
 */
(function () {
    'use strict';

    function initDashboardFilters() {
        var panel = document.getElementById('o_winners_filter_panel');
        var grid = document.getElementById('o_winners_product_grid');
        if (!panel || !grid) {
            return;
        }

        var categorySelect = document.getElementById('o_winners_filter_category');
        var countrySelect = document.getElementById('o_winners_filter_country');
        var priceMaxInput = document.getElementById('o_winners_filter_price_max');
        var sourceSelect = document.getElementById('o_winners_filter_source');
        var resetBtn = document.getElementById('o_winners_filter_reset');

        function escapeHtml(value) {
            var div = document.createElement('div');
            div.textContent = value == null ? '' : String(value);
            return div.innerHTML;
        }

        function renderProductCard(p) {
            var col = document.createElement('div');
            col.className = 'col-md-4 col-sm-6 mb-4';

            var categoryHtml = p.category
                ? '<span class="o_winners_product_card__category">' + escapeHtml(p.category) + '</span>'
                : '';
            var countryHtml = p.country
                ? '<span class="o_winners_product_card__country">' + escapeHtml(p.country) + '</span>'
                : '';
            var scoreValue = (typeof p.score === 'number') ? p.score : 0.0;
            var scoreTier = scoreValue >= 75 ? '--high' : (scoreValue >= 50 ? '--mid' : '--low');
            var scoreText = scoreValue.toFixed(1);

            // Structure alignée sur produits_tendance.template_product_cards
            // (mêmes classes, y compris le modificateur de palier de score)
            // pour que le rendu JS soit identique au rendu serveur initial.
            col.innerHTML =
                '<a href="/product/' + encodeURIComponent(p.id) + '" class="o_winners_product_card">' +
                    categoryHtml +
                    '<h3 class="o_winners_product_card__name">' + escapeHtml(p.name) + '</h3>' +
                    '<div class="o_winners_product_card__footer">' +
                        '<span class="o_winners_product_card__score o_winners_product_card__score' + scoreTier + '">' +
                            scoreText +
                        '</span>' +
                        countryHtml +
                    '</div>' +
                '</a>';
            return col;
        }

        function renderEmptyState() {
            var col = document.createElement('div');
            col.className = 'col-12';
            var alert = document.createElement('div');
            alert.className = 'alert alert-info text-center o_winners_product_grid__empty';
            alert.textContent = 'Aucun produit ne correspond à ces filtres pour le moment.';
            col.appendChild(alert);
            return col;
        }

        function renderProducts(products) {
            grid.innerHTML = '';
            if (!products || !products.length) {
                grid.appendChild(renderEmptyState());
                return;
            }
            products.forEach(function (p) {
                grid.appendChild(renderProductCard(p));
            });
        }

        // Compteur pour ignorer les réponses obsolètes si l'utilisateur
        // change les filtres plus vite que le réseau ne répond.
        var requestToken = 0;

        function applyFilters() {
            var params = new URLSearchParams();
            if (categorySelect && categorySelect.value) {
                params.set('category_id', categorySelect.value);
            }
            if (countrySelect && countrySelect.value) {
                params.set('country', countrySelect.value);
            }
            if (priceMaxInput && priceMaxInput.value) {
                params.set('price_max', priceMaxInput.value);
            }
            if (sourceSelect && sourceSelect.value) {
                params.set('source', sourceSelect.value);
            }

            var currentToken = ++requestToken;
            grid.classList.add('o_winners_product_grid--loading');

            fetch('/api/dashboard/filter?' + params.toString(), {
                method: 'GET',
                headers: { 'Accept': 'application/json' },
            })
                .then(function (response) { return response.json(); })
                .then(function (data) {
                    if (currentToken !== requestToken) {
                        return; // une requête plus récente est en cours
                    }
                    if (data && data.status === 'success') {
                        renderProducts(data.products);
                    }
                })
                .catch(function () {
                    // En cas d'échec réseau, on laisse la grille existante
                    // affichée plutôt que de la vider.
                })
                .finally(function () {
                    if (currentToken === requestToken) {
                        grid.classList.remove('o_winners_product_grid--loading');
                    }
                });
        }

        // Le prix max est un input texte/numérique : on écoute "input" (frappe
        // en direct) mais avec un léger debounce pour éviter une requête par
        // caractère tapé.
        var priceMaxDebounceTimer = null;
        function applyFiltersDebounced() {
            if (priceMaxDebounceTimer) {
                clearTimeout(priceMaxDebounceTimer);
            }
            priceMaxDebounceTimer = setTimeout(applyFilters, 400);
        }

        if (categorySelect) {
            categorySelect.addEventListener('change', applyFilters);
        }
        if (countrySelect) {
            countrySelect.addEventListener('change', applyFilters);
        }
        if (priceMaxInput) {
            priceMaxInput.addEventListener('input', applyFiltersDebounced);
        }
        if (sourceSelect) {
            sourceSelect.addEventListener('change', applyFilters);
        }
        if (resetBtn) {
            resetBtn.addEventListener('click', function () {
                if (categorySelect) { categorySelect.value = ''; }
                if (countrySelect) { countrySelect.value = ''; }
                if (priceMaxInput) { priceMaxInput.value = ''; }
                if (sourceSelect) { sourceSelect.value = ''; }
                applyFilters();
            });
        }
    }

    // Si le DOM est déjà chargé au moment où ce script s'exécute (cas
    // fréquent sur les pages Odoo, où les bundles JS peuvent être injectés
    // après DOMContentLoaded), on initialise immédiatement. Sinon on
    // attend l'événement comme avant.
    if (document.readyState === 'loading') {
        document.addEventListener('DOMContentLoaded', initDashboardFilters);
    } else {
        initDashboardFilters();
    }
})();