/**
 * EXOCOMS — Interception ciblée bouton "Shop"
 * static/src/js/shop_redirect.js
 *
 * Intercepte UNIQUEMENT le bouton "Shop" dans la page panier
 * qui pointe exactement vers /shop
 * Tout le reste fonctionne normalement
 */

(function () {
    'use strict';

    document.addEventListener('click', function (e) {

        var link = e.target.closest('a[href]');
        if (!link) return;

        var href = link.getAttribute('href') || '';
        var text = link.textContent.trim().toLowerCase();

        /* Intercepte UNIQUEMENT le lien exact /shop avec le texte "Shop" */
        var isShopBtn = (
            href === '/shop' &&
            text === 'shop'
        );

        if (!isShopBtn) return;

        e.preventDefault();
        e.stopPropagation();

        var iframe = document.getElementById('exo-shop-frame');

        if (iframe) {
            /* Sur le dashboard — charge dans l'iframe */
            iframe.src = '/shop';
            iframe.scrollIntoView({ behavior: 'smooth', block: 'start' });
        } else {
            /* Sur une autre page — va sur l'accueil */
            sessionStorage.setItem('exo_shop_url', '/shop');
            window.location.href = '/';
        }

    }, true);

    /* Au chargement — charge l'URL stockée */
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