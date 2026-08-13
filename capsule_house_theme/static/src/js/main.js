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

    /**
     * Valeurs dynamiques du hero (note, comptages, produits vedettes) —
     * v19.0.1.0.60, voir README "Cause réelle #3 — contenu dynamique dans
     * le hero". hero.xml ne contient plus aucun t-esc/t-if : ces valeurs
     * sont injectées ICI, après le chargement de la page, exactement
     * comme les snippets dynamiques natifs d'Odoo (doc officielle
     * "Building blocks > Dynamic Content templates"). Objectif : que
     * l'arch de hero.xml reste 100% statique, condition nécessaire pour
     * qu'Odoo marque la <section> du hero comme un bloc sélectionnable
     * (data-oe-model, panneau Style) — un sous-arbre contenant une
     * expression dynamique n'est jamais marqué comme "bloc" par Odoo,
     * confirmé par comparaison directe avec un bloc natif Odoo ET avec
     * le hero d'exocoms_theme (aucun contenu dynamique dans son arch).
     *
     * Dégradation gracieuse : en cas d'échec du fetch (réseau, route
     * indisponible...), le hero reste utilisable tel quel (aucune donnée
     * fabriquée en JS de secours, les placeholders restent simplement
     * masqués/à zéro).
     */
    function initHeroDynamicContent() {
        var hero = document.querySelector('.ch-hero');
        if (!hero) return;

        fetch('/capsule-house/hero-data.json', { headers: { 'Accept': 'application/json' } })
            .then(function (response) {
                if (!response.ok) { throw new Error('HTTP ' + response.status); }
                return response.json();
            })
            .then(function (data) {
                applyHeroRatingBadge(hero, data);
                applyHeroStats(hero, data);
                applyHeroFloatCards(hero, data);
            })
            .catch(function () {
                // Silencieux : dégradation gracieuse, voir docstring ci-dessus.
            });
    }

    // v19.0.1.0.61 : le badge reste toujours affiché, même sans aucun avis
    // publié (affiche "0" plutôt que de rester masqué) — retour client.
    function applyHeroRatingBadge(hero, data) {
        var badge = hero.querySelector('[data-ch-rating-badge]');
        if (!badge) return;
        var valueEl = badge.querySelector('[data-ch-rating-value]');
        var messageEl = badge.querySelector('[data-ch-rating-message]');
        if (valueEl) valueEl.textContent = (data.rating_value != null) ? data.rating_value : 0;
        if (messageEl) messageEl.textContent = data.rating_message || '';
        badge.classList.remove('d-none');
    }

    function applyHeroStats(hero, data) {
        var publishedEl = hero.querySelector('[data-ch-stat="published_products_count"]');
        if (publishedEl) publishedEl.textContent = data.published_products_count || 0;

        if (data.units_installed_count) {
            var unitsBlock = hero.querySelector('[data-ch-stat-block="units_installed_count"]');
            var unitsValueEl = hero.querySelector('[data-ch-stat="units_installed_count"]');
            if (unitsValueEl) unitsValueEl.textContent = data.units_installed_count;
            if (unitsBlock) unitsBlock.classList.remove('d-none');
        }
    }

    function applyHeroFloatCards(hero, data) {
        var container = hero.querySelector('[data-ch-float-cards]');
        var products = data.featured_products || [];
        if (!container || !products.length) return;

        var labelNew = container.getAttribute('data-ch-label-new') || 'New';
        var labelPromo = container.getAttribute('data-ch-label-promo') || 'Sale';

        products.forEach(function (product, index) {
            var card = document.createElement('a');
            card.href = product.url;
            card.className = 'ch-hero-float-card' + (index === 1 ? ' ch-hero-float-card-2' : '');

            if (product.is_new) {
                var newBadge = document.createElement('span');
                newBadge.className = 'ch-hero-float-badge ch-hero-float-badge-new';
                newBadge.textContent = labelNew;
                card.appendChild(newBadge);
            }
            if (product.has_discount) {
                var promoBadge = document.createElement('span');
                promoBadge.className = 'ch-hero-float-badge ch-hero-float-badge-promo';
                promoBadge.textContent = labelPromo;
                card.appendChild(promoBadge);
            }

            var imgWrap = document.createElement('div');
            imgWrap.className = 'ch-hero-float-img';
            var img = document.createElement('img');
            img.src = product.image_url;
            img.alt = product.name;
            imgWrap.appendChild(img);
            card.appendChild(imgWrap);

            var body = document.createElement('div');
            body.className = 'ch-hero-float-body';
            var nameEl = document.createElement('span');
            nameEl.className = 'ch-hero-float-name';
            nameEl.textContent = product.name;
            var priceEl = document.createElement('span');
            priceEl.className = 'ch-hero-float-price';
            priceEl.textContent = product.price_formatted;
            body.appendChild(nameEl);
            body.appendChild(priceEl);
            card.appendChild(body);

            container.appendChild(card);
        });

        if (data.cart_product_id) {
            var cartForm = hero.querySelector('[data-ch-cart-shortcut]');
            if (cartForm) {
                var productIdInput = cartForm.querySelector('[name="product_id"]');
                var csrfInput = cartForm.querySelector('[name="csrf_token"]');
                if (productIdInput) productIdInput.value = data.cart_product_id;
                if (csrfInput) csrfInput.value = data.csrf_token || '';
                cartForm.classList.remove('d-none');
            }
        }
    }

    /**
     * Défilement automatique du carousel témoignages (.ch-testimonials-track,
     * voir views/partials/home_trust.xml) — v19.0.1.0.66, repris
     * d'exocoms_theme (features.xml) mais déplacé ici plutôt que laissé en
     * <script> inline dans le template QWeb, pour rester cohérent avec le
     * reste de ce module (tout le JS du thème vit dans main.js, jamais
     * dans les vues). Pause au survol, boucle infinie par duplication des
     * cartes. Ne fait rien si moins de 2 avis (rien à faire défiler).
     */
    function initTestimonialsCarousel() {
        var track = document.getElementById('ch-testimonials-track');
        if (!track || track.dataset.chInit) return;
        track.dataset.chInit = '1';

        var originals = Array.prototype.slice.call(track.children);
        if (originals.length < 2) return;
        originals.forEach(function (node) { track.appendChild(node.cloneNode(true)); });

        var paused = false;
        track.addEventListener('mouseenter', function () { paused = true; });
        track.addEventListener('mouseleave', function () { paused = false; });

        var pos = track.scrollLeft;
        function step() {
            if (!paused) {
                pos += 0.6;
                var half = track.scrollWidth / 2;
                if (half > 0 && pos >= half) pos -= half;
                track.scrollLeft = pos;
            }
            window.requestAnimationFrame(step);
        }
        window.requestAnimationFrame(step);
    }

    function init() {
        initScrollReveal();
        initHeroDynamicContent();
        initTestimonialsCarousel();
    }

    if (document.readyState === 'loading') {
        document.addEventListener('DOMContentLoaded', init);
    } else {
        init();
    }
    document.addEventListener('page:loaded', init);
})();
