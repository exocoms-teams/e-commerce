/**
 * capsule_house_theme — JavaScript principal
 *
 * CORRECTIF — voir README "Header natif comme sur exocoms_theme" :
 * ce fichier contenait initBurger()/initNavActive(), du JS maison pour
 * piloter le menu mobile et l'état "actif" de notre ancien header
 * custom (#chBurger, #chNav, .ch-nav-link). Le header est désormais le
 * header#top natif Odoo (voir layout.xml/header.xml/layout.css) : le
 * menu mobile (offcanvas) et la mise en surbrillance du lien actif
 * sont gérés nativement par Odoo lui-même, plus besoin de JS ici.
 */
(function () {
    'use strict';

    function initScrollReveal() {
        if (!('IntersectionObserver' in window)) return;
        var targets = document.querySelectorAll('.ch-product-card');
        if (!targets.length) return;
        var obs = new IntersectionObserver(function (entries) {
            entries.forEach(function (entry) {
                if (entry.isIntersecting) {
                    entry.target.style.opacity = '1';
                    entry.target.style.transform = 'translateY(0)';
                    obs.unobserve(entry.target);
                }
            });
        }, { threshold: 0.1, rootMargin: '0px 0px -30px 0px' });

        targets.forEach(function (el, i) {
            el.style.opacity = '0';
            el.style.transform = 'translateY(14px)';
            el.style.transition = 'opacity 0.45s ease ' + (i * 0.06) + 's, transform 0.45s ease ' + (i * 0.06) + 's';
            obs.observe(el);
        });
    }

    function init() {
        initBurger();
        initNavActive();
        initScrollReveal();
    }

    if (document.readyState === 'loading') {
        document.addEventListener('DOMContentLoaded', init);
    } else {
        init();
    }
    document.addEventListener('page:loaded', init);
})();
