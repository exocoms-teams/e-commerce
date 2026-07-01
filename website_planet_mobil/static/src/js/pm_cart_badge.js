// Planet Mobil — mise à jour badge panier (plain script, pas de @odoo-module)
(function () {
    'use strict';

    console.log('[PM] pm_cart_badge.js chargé');

    function updateBadge(qty) {
        var n = parseInt(qty) || 0;
        // Cible tous les éléments .o_cart_quantity sur la page
        document.querySelectorAll('.o_cart_quantity').forEach(function (el) {
            el.textContent = n;
            el.classList.toggle('d-none', n === 0);
        });
    }

    // --- Stratégie 1 : intercepter fetch (Odoo 17+) ---
    var _fetch = window.fetch;
    window.fetch = function (input, init) {
        var url = typeof input === 'string' ? input : (input && input.url) || '';
        var promise = _fetch.apply(this, arguments);
        if (/\/shop\/cart/.test(url)) {
            promise.then(function (response) {
                response.clone().json().then(function (data) {
                    if (typeof data.cart_quantity === 'number') {
                        updateBadge(data.cart_quantity);
                    }
                }).catch(function () {});
            }).catch(function () {});
        }
        return promise;
    };

    // --- Stratégie 2 : intercepter XMLHttpRequest (fallback) ---
    var _open = XMLHttpRequest.prototype.open;
    var _send = XMLHttpRequest.prototype.send;
    XMLHttpRequest.prototype.open = function (method, url) {
        this._pmUrl = url;
        return _open.apply(this, arguments);
    };
    XMLHttpRequest.prototype.send = function () {
        if (this._pmUrl && /\/shop\/cart/.test(this._pmUrl)) {
            this.addEventListener('load', function () {
                try {
                    var data = JSON.parse(this.responseText);
                    if (typeof data.cart_quantity === 'number') {
                        updateBadge(data.cart_quantity);
                    }
                } catch (e) {}
            });
        }
        return _send.apply(this, arguments);
    };

    // --- Stratégie 3 : clic sur "Ajouter au panier" → requête /shop/cart/quantity ---
    document.addEventListener('click', function (e) {
        var btn = e.target.closest(
            '#add_to_cart, .o_add_cart_btn, [data-action="add_to_cart"], .a-submit'
        );
        if (!btn) return;
        // Attendre qu'Odoo ait traité la commande puis rafraîchir
        [600, 1400].forEach(function (delay) {
            setTimeout(function () {
                _fetch('/shop/cart/quantity', { headers: { 'X-Requested-With': 'XMLHttpRequest' } })
                    .then(function (r) { return r.json(); })
                    .then(function (data) {
                        var qty = typeof data === 'number' ? data : (data && data.cart_quantity);
                        if (qty !== undefined) updateBadge(qty);
                    })
                    .catch(function () {});
            }, delay);
        });
    });

})();
