/** @odoo-module **/
/**
 * Planet Mobil — mise à jour dynamique du badge panier personnalisé.
 * Odoo 19 utilise un composant Owl pour le panier natif ; comme on l'a remplacé
 * par du HTML custom, ce script intercepte les réponses cart pour mettre à jour
 * notre badge (.pm-cart-badge.o_cart_quantity).
 */
(function () {
    'use strict';

    function updateBadge(qty) {
        const badge = document.querySelector('.pm-cart-badge.o_cart_quantity');
        if (!badge) return;
        badge.textContent = qty;
        badge.classList.toggle('d-none', qty === 0);
    }

    function tryParse(text) {
        try { return JSON.parse(text); } catch (e) { return null; }
    }

    const CART_URLS = ['/shop/cart/update', '/shop/cart/update_json'];
    const isCartUrl = (url) => CART_URLS.some(u => String(url).includes(u));

    // --- Intercept fetch ---
    const _fetch = window.fetch;
    window.fetch = function (input, init) {
        const url = (typeof input === 'string') ? input : (input && input.url) || '';
        return _fetch.apply(this, arguments).then(function (response) {
            if (isCartUrl(url)) {
                response.clone().json().then(function (data) {
                    if (typeof data.cart_quantity === 'number') {
                        updateBadge(data.cart_quantity);
                    }
                }).catch(function () {});
            }
            return response;
        });
    };

    // --- Intercept XMLHttpRequest (fallback) ---
    const _open = XMLHttpRequest.prototype.open;
    const _send = XMLHttpRequest.prototype.send;

    XMLHttpRequest.prototype.open = function (method, url) {
        this._pmUrl = url;
        return _open.apply(this, arguments);
    };

    XMLHttpRequest.prototype.send = function () {
        if (isCartUrl(this._pmUrl)) {
            this.addEventListener('load', function () {
                const data = tryParse(this.responseText);
                if (data && typeof data.cart_quantity === 'number') {
                    updateBadge(data.cart_quantity);
                }
            });
        }
        return _send.apply(this, arguments);
    };
})();
