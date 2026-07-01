// Planet Mobil — badge panier dynamique
(function () {
    'use strict';

    function updateBadge(qty) {
        var n = parseInt(qty) || 0;
        document.querySelectorAll('.o_cart_quantity').forEach(function (el) {
            el.textContent = n;
            if (n === 0) {
                el.classList.remove('pm-cart-badge');
                el.style.setProperty('display', 'none', 'important');
            } else {
                el.classList.add('pm-cart-badge');
                el.style.removeProperty('display');
            }
        });
    }

    // Intercepte fetch (Odoo 17+)
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

    // Intercepte XHR (fallback)
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

    // Clic sur "Ajouter au panier" → relit la quantité après délai
    document.addEventListener('click', function (e) {
        var btn = e.target.closest('#add_to_cart, .o_add_cart_btn, [data-action="add_to_cart"], .a-submit');
        if (!btn) return;
        [700, 1500].forEach(function (delay) {
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
