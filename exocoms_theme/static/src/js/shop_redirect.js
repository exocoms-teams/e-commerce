/**
 * EXOCOMS — Interception globale TOUT /shop sans exception
 * static/src/js/shop_redirect.js
 */

(function () {
    'use strict';

    document.addEventListener('click', function (e) {

        var link = e.target.closest('a[href]');
        if (!link) return;

        var href = link.getAttribute('href') || '';

        /* Intercepte TOUT ce qui contient /shop — sans exception */
        if (!href.includes('/shop')) return;

        var iframe = document.getElementById('exo-shop-frame');

        if (!iframe) {
            /* Pas sur la page dashboard — redirige vers l'accueil avec l'URL */
            e.preventDefault();
            e.stopPropagation();
            window.location.href = '/?shop_url=' + encodeURIComponent(href);
            return;
        }

        /* Sur la page dashboard — charge dans l'iframe */
        e.preventDefault();
        e.stopPropagation();

        iframe.src = href;
        iframe.scrollIntoView({ behavior: 'smooth', block: 'start' });

    }, true);

    /* Si on arrive avec ?shop_url= dans l'URL */
    document.addEventListener('DOMContentLoaded', function () {
        var params = new URLSearchParams(window.location.search);
        var shopUrl = params.get('shop_url');

        if (shopUrl) {
            window.history.replaceState({}, '', '/');
            var iframe = document.getElementById('exo-shop-frame');
            if (iframe) {
                iframe.src = decodeURIComponent(shopUrl);
            }
        }
    });

})();