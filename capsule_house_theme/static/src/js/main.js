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
     * Section "avis clients" de l'accueil (v19.0.1.0.100, voir
     * views/partials/home_testimonials.xml). Même principe que
     * initHeroDynamicContent() ci-dessus : l'arch reste 100% statique
     * (section masquée par défaut, data-ch-testimonials-section), le
     * contenu réel (jusqu'à 3 VRAIS avis publiés) est injecté ici après
     * coup. Dégradation gracieuse : en cas d'échec du fetch OU si aucun
     * avis n'est encore publié, la section reste masquée (jamais de
     * témoignage fabriqué en secours).
     */
    function initTestimonialsSection() {
        var section = document.querySelector('[data-ch-testimonials-section]');
        if (!section) return;
        var grid = section.querySelector('[data-ch-testimonials-grid]');
        if (!grid) return;

        fetch('/capsule-house/testimonials-data.json', { headers: { 'Accept': 'application/json' } })
            .then(function (response) {
                if (!response.ok) { throw new Error('HTTP ' + response.status); }
                return response.json();
            })
            .then(function (data) {
                var items = data.items || [];
                if (!items.length) return;
                items.forEach(function (item) {
                    grid.appendChild(buildTestimonialCard(item));
                });
                section.classList.remove('d-none');
            })
            .catch(function () {
                // Silencieux : dégradation gracieuse, section reste masquée.
            });
    }

    // Avatar = initiale du vrai nom (même convention que .ch-avis-avatar
    // sur /avis, voir avis_content.xml) — jamais une fausse photo.
    function buildTestimonialCard(item) {
        var card = document.createElement('div');
        card.className = 'ch-testi-card';

        var head = document.createElement('div');
        head.className = 'ch-testi-card-head';

        var avatar = document.createElement('div');
        avatar.className = 'ch-testi-avatar';
        avatar.textContent = item.initial || '?';
        head.appendChild(avatar);

        var meta = document.createElement('div');
        var nameEl = document.createElement('div');
        nameEl.className = 'ch-testi-name';
        nameEl.textContent = item.name || '';
        meta.appendChild(nameEl);

        var stars = document.createElement('div');
        stars.className = 'ch-testi-stars';
        for (var i = 1; i <= 5; i++) {
            var star = document.createElement('i');
            star.className = 'fa ' + (i <= (item.rating || 0) ? 'fa-star' : 'fa-star-o');
            stars.appendChild(star);
        }
        meta.appendChild(stars);
        head.appendChild(meta);
        card.appendChild(head);

        var text = document.createElement('p');
        text.className = 'ch-testi-text';
        text.textContent = item.comment || '';
        card.appendChild(text);

        if (item.product) {
            var tag = document.createElement('span');
            tag.className = 'ch-testi-product-tag';
            tag.textContent = item.product;
            card.appendChild(tag);
        }

        return card;
    }

    /**
     * Section "moyens de paiement" de l'accueil (v19.0.1.0.100, voir
     * views/partials/home_payment_methods.xml). Même principe : section
     * masquée par défaut, peuplée UNIQUEMENT avec les payment.provider
     * réellement à l'état 'enabled' (voir controllers/main.py,
     * payment_methods_data()). Reste masquée tant qu'aucun n'est
     * configuré — jamais de logo de marque non vérifié.
     */
    function initPaymentMethodsSection() {
        var section = document.querySelector('[data-ch-payment-section]');
        if (!section) return;
        var badges = section.querySelector('[data-ch-payment-badges]');
        if (!badges) return;

        fetch('/capsule-house/payment-methods-data.json', { headers: { 'Accept': 'application/json' } })
            .then(function (response) {
                if (!response.ok) { throw new Error('HTTP ' + response.status); }
                return response.json();
            })
            .then(function (data) {
                var items = data.items || [];
                if (!items.length) return;
                items.forEach(function (item) {
                    var badge = document.createElement('span');
                    badge.className = 'ch-payment-badge';
                    var icon = document.createElement('i');
                    icon.className = 'fa fa-credit-card';
                    badge.appendChild(icon);
                    var label = document.createElement('span');
                    label.textContent = item.name || '';
                    badge.appendChild(label);
                    badges.appendChild(badge);
                });
                section.classList.remove('d-none');
            })
            .catch(function () {
                // Silencieux : dégradation gracieuse, section reste masquée.
            });
    }

    function init() {
        initScrollReveal();
        initHeroDynamicContent();
        initTestimonialsSection();
        initPaymentMethodsSection();
    }

    if (document.readyState === 'loading') {
        document.addEventListener('DOMContentLoaded', init);
    } else {
        init();
    }
    document.addEventListener('page:loaded', init);
})();
