/**
 * EXOCOMS — Interception globale des liens /shop
 * Fichier: static/src/js/shop_redirect.js
 *
 * Tout lien qui pointe vers /shop ou /shop/category/...
 * charge dans l'iframe du dashboard au lieu d'ouvrir une nouvelle page.
 */

(function () {
    'use strict';

    document.addEventListener('click', function (e) {

        var link = e.target.closest('a[href]');
        if (!link) return;

        var href = link.getAttribute('href') || '';

        /* Cible uniquement les liens shop — pas le panier, pas les produits individuels */
        var isShopLink = (
            href === '/shop' ||
            href.startsWith('/shop?') ||
            href.startsWith('/shop/page/') ||
            href.startsWith('/shop/category/')
        );

        if (!isShopLink) return;

        /* Cherche l'iframe du dashboard */
        var iframe = document.getElementById('exo-shop-frame');

        if (!iframe) return; /* Si pas sur la page du dashboard, comportement normal */

        e.preventDefault();
        e.stopPropagation();

        /* Charge l'URL dans l'iframe */
        iframe.src = href;

        /* Scroll vers l'iframe */
        iframe.scrollIntoView({ behavior: 'smooth', block: 'start' });

    }, true); /* capture=true — intercepte avant tout autre handler */

})();