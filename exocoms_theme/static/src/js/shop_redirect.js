/**
 * EXOCOMS — Interception bouton Shop
 * static/src/js/shop_redirect.js
 */

(function () {
    'use strict';

    document.addEventListener('click', function (e) {

        var link = e.target.closest('a[href]');
        if (!link) return;

        var href = link.getAttribute('href') || '';

        /* Intercepte uniquement les liens /shop */
        if (!href.includes('/shop')) return;

        e.preventDefault();
        e.stopPropagation();

        var iframe = document.getElementById('exo-shop-frame');

        if (iframe) {
            /* Déjà sur le dashboard — met à jour l'iframe seulement */
            iframe.src = href;
            iframe.scrollIntoView({ behavior: 'smooth', block: 'start' });
        } else {
            /* Pas sur le dashboard — va sur l'accueil sans recharger tout */
            if (window.location.pathname === '/') {
                /* Déjà sur l'accueil mais iframe pas encore là — attend */
                var tries = 0;
                var wait = setInterval(function () {
                    var fr = document.getElementById('exo-shop-frame');
                    if (fr) {
                        clearInterval(wait);
                        fr.src = href;
                        fr.scrollIntoView({ behavior: 'smooth', block: 'start' });
                    }
                    if (++tries > 20) clearInterval(wait);
                }, 100);
            } else {
                /* Sur une autre page — stocke l'URL et va à l'accueil */
                sessionStorage.setItem('exo_shop_url', href);
                window.location.href = '/';
            }
        }

    }, true);

    /* Au chargement de l'accueil — charge l'URL stockée dans l'iframe */
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