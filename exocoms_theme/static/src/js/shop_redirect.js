/**
 * EXOCOMS — shop_redirect.js
 * Intercepte le bouton Shop et la recherche
 * pour charger dans l'iframe de la page boutique
 */

(function () {
    'use strict';

    function loadInIframe(url) {
        var iframe = document.getElementById('exo-shop-frame');
        if (iframe) {
            iframe.src = url;
            iframe.scrollIntoView({ behavior: 'smooth', block: 'start' });
        } else {
            sessionStorage.setItem('exo_shop_url', url);
            window.location.href = '/boutique';
        }
    }

    /* Bouton "Shop" exact */
    document.addEventListener('click', function (e) {
        var link = e.target.closest('a[href]');
        if (!link) return;
        var href = link.getAttribute('href') || '';
        if (href === '/shop' && link.textContent.trim().toLowerCase() === 'shop') {
            e.preventDefault();
            e.stopPropagation();
            loadInIframe('/shop');
        }
    }, true);

    /* Formulaire de recherche */
    document.addEventListener('submit', function (e) {
        var form = e.target;
        if (!form) return;
        var action = form.getAttribute('action') || '';
        if (!action.includes('/shop')) return;
        e.preventDefault();
        e.stopPropagation();
        var input = form.querySelector('input[name="search"], input[type="search"]');
        var val = input ? input.value.trim() : '';
        loadInIframe('/shop' + (val ? '?search=' + encodeURIComponent(val) : ''));
    }, true);

    /* Bouton Rechercher */
    document.addEventListener('click', function (e) {
        var btn = e.target.closest('button[type="submit"]');
        if (!btn) return;
        var form = btn.closest('form');
        if (!form) return;
        var action = form.getAttribute('action') || '';
        if (!action.includes('/shop')) return;
        e.preventDefault();
        e.stopPropagation();
        var input = form.querySelector('input[name="search"], input[type="search"]');
        var val = input ? input.value.trim() : '';
        loadInIframe('/shop' + (val ? '?search=' + encodeURIComponent(val) : ''));
    }, true);

    /* Restaure l'URL au chargement */
    document.addEventListener('DOMContentLoaded', function () {
        var shopUrl = sessionStorage.getItem('exo_shop_url');
        if (shopUrl) {
            sessionStorage.removeItem('exo_shop_url');
            var iframe = document.getElementById('exo-shop-frame');
            if (iframe) iframe.src = shopUrl;
        }
    });

})();