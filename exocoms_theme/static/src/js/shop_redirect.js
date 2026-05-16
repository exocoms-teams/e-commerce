/**
 * EXOCOMS — Interception search + bouton Shop
 * static/src/js/shop_redirect.js
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
            window.location.href = '/';
        }
    }

    /* === Intercepte les clics sur liens /shop === */
    document.addEventListener('click', function (e) {
        var link = e.target.closest('a[href]');
        if (!link) return;

        var href = link.getAttribute('href') || '';

        /* Bouton Shop exactement */
        if (href === '/shop' && link.textContent.trim().toLowerCase() === 'shop') {
            e.preventDefault();
            e.stopPropagation();
            loadInIframe('/shop');
            return;
        }
    }, true);

    /* === Intercepte la soumission du formulaire de recherche === */
    document.addEventListener('submit', function (e) {
        var form = e.target;
        if (!form) return;

        /* Formulaire qui pointe vers /shop */
        var action = form.getAttribute('action') || '';
        if (!action.includes('/shop') && !action.includes('shop')) return;

        e.preventDefault();
        e.stopPropagation();

        /* Récupère la valeur du champ search */
        var input = form.querySelector('input[name="search"], input[type="search"], input[type="text"]');
        var searchVal = input ? input.value.trim() : '';

        var url = '/shop' + (searchVal ? '?search=' + encodeURIComponent(searchVal) : '');
        loadInIframe(url);

    }, true);

    /* === Intercepte aussi le bouton "Rechercher" par clic === */
    document.addEventListener('click', function (e) {
        var btn = e.target.closest('button[type="submit"], input[type="submit"]');
        if (!btn) return;

        var form = btn.closest('form');
        if (!form) return;

        var action = form.getAttribute('action') || '';
        if (!action.includes('/shop') && !action.includes('shop')) return;

        e.preventDefault();
        e.stopPropagation();

        var input = form.querySelector('input[name="search"], input[type="search"], input[type="text"]');
        var searchVal = input ? input.value.trim() : '';

        var url = '/shop' + (searchVal ? '?search=' + encodeURIComponent(searchVal) : '');
        loadInIframe(url);

    }, true);

    /* === Au chargement — restaure l'URL stockée === */
    document.addEventListener('DOMContentLoaded', function () {
        var shopUrl = sessionStorage.getItem('exo_shop_url');
        if (shopUrl) {
            sessionStorage.removeItem('exo_shop_url');
            var iframe = document.getElementById('exo-shop-frame');
            if (iframe) {
                iframe.src = shopUrl;
            }
        }
    });

})();