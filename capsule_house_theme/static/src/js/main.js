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
        if (window.matchMedia('(prefers-reduced-motion: reduce)').matches) return;
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

    function initFeaturedProductsCarousel() {
        const carousel = document.getElementById('ch_bestsellers_carousel');
        if (!carousel || carousel.dataset.chBound) return;

        const viewport = carousel.querySelector('.ch-bestsellers-viewport');
        const track = carousel.querySelector('.ch-bestsellers-track');
        if (!viewport || !track) {
            throw new Error('Featured products carousel track was not found.');
        }

        const originals = [...track.children];
        const count = originals.length;
        if (count < 2) return;

        const SPEED = 28;            // px/s
        const GROUP_SIZE = 4;        // slides par clic prev/next
        const GROUP_DURATION = 500;  // ms
        const CARD = '.ch-product-card';
        const reducedMotion = window.matchMedia('(prefers-reduced-motion: reduce)');

        const mod = (n, m) => ((n % m) + m) % m;
        const buffer = Math.max(
            4,
            Math.ceil(viewport.clientWidth / originals[0].getBoundingClientRect().width)
        ) + 4;

        // --- Clones (buffer avant + après pour la boucle infinie) ---
        const cloneAt = (i) => {
            const clone = originals[mod(i, count)].cloneNode(true);
            clone.querySelector(CARD)?.removeAttribute('style');
            return clone;
        };
        track.prepend(...Array.from({ length: buffer }, (_, i) => cloneAt(i - buffer)));
        track.append(...Array.from({ length: buffer }, (_, i) => cloneAt(i)));
        const slides = [...track.children];

        // --- État ---
        let step = 0;          // largeur d'une slide + gap
        let cycle = 0;         // largeur d'un cycle complet
        let offset = 0;
        let raf = 0;
        let lastTime = null;
        let hovered = false;
        let anim = null;       // { from, to, startTime } pendant un clic prev/next
        let visibleKey = '';

        const isPaused = () => hovered || reducedMotion.matches;

        const measure = () => {
            const gap = parseFloat(getComputedStyle(track).columnGap) || 0;
            step = slides[0].getBoundingClientRect().width + gap;
            cycle = count * step;
        };

        // Ramène l'offset dans le cycle central (celui des slides originales)
        const wrap = () => {
            const min = buffer * step;
            offset = min + mod(offset - min, cycle);
        };

        // Seules les slides visibles sont focusables / lues par les lecteurs d'écran
        const updateAccessibility = () => {
            const first = Math.floor(offset / step);
            const end = Math.ceil((offset + viewport.clientWidth) / step);
            const key = `${first}:${end}`;
            if (key === visibleKey) return;
            visibleKey = key;
            slides.forEach((slide, i) => slide.toggleAttribute('inert', i < first || i >= end));
        };

        const render = () => {
            track.style.transform = `translate3d(${-offset}px, 0, 0)`;
            updateAccessibility();
        };

        // --- Boucle d'animation unique ---
        const tick = (time) => {
            raf = 0;
            if (!anim && isPaused()) {
            lastTime = null;
            return;
            }

            if (anim) {
            if (anim.startTime === null) anim.startTime = time;
            const progress = Math.min((time - anim.startTime) / GROUP_DURATION, 1);
            offset = anim.from + (anim.to - anim.from) * (1 - (1 - progress) ** 3);
            if (progress === 1) {
                anim = null;
                wrap();
            }
            } else {
            const dt = lastTime === null ? 0 : Math.min(time - lastTime, 50);
            offset += (SPEED * dt) / 1000;
            wrap();
            }

            lastTime = time;
            render();
            raf = requestAnimationFrame(tick);
        };

        const start = () => {
            if (!raf) raf = requestAnimationFrame(tick);
        };

        const slideBy = (direction) => {
            if (anim) return;
            const distance = direction * GROUP_SIZE * step;
            if (reducedMotion.matches) {
            offset += distance;
            wrap();
            render();
            return;
            }
            anim = { from: offset, to: offset + distance, startTime: null };
            start();
        };

        // --- Événements ---
        viewport.addEventListener('pointerover', (e) => {
            hovered = Boolean(e.target.closest(CARD));
            if (!hovered) start();
        });
        viewport.addEventListener('pointerleave', () => {
            hovered = false;
            start();
        });

        carousel.querySelectorAll('[data-ch-slide]').forEach((button) => {
            button.addEventListener('click', () =>
            slideBy(button.dataset.chSlide === 'next' ? 1 : -1)
            );
        });

        window.addEventListener('resize', () => {
            const position = (anim ? anim.to : offset) / step; // position en nombre de slides
            anim = null;
            measure();
            offset = position * step;
            wrap();
            visibleKey = '';
            render();
            start();
        });

        reducedMotion.addEventListener('change', start);

        // --- Init ---
        measure();
        offset = buffer * step;
        render();
        carousel.dataset.chBound = '1';
        start();
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

        /**
     * Ajoute un produit au panier via /shop/cart/add en JSON-RPC (route
     * native website_sale, type='jsonrpc' depuis Odoo 19 — un simple
     * <form method="post"> classique est rejeté avec "Unsupported Media
     * Type"). Voir raccourci "Ajouter au panier" du hero,
     * data-ch-cart-shortcut.
     */
    function addToCartJsonRpc(templateId, variantId, button) {
        if (button) {
            button.disabled = true;
            button.dataset.chOriginalHtml = button.innerHTML;
            button.innerHTML = '<i class="fa fa-check"/> Ajouté !';
        }
        fetch('/shop/cart/add', {
            method: 'POST',
            headers: { 'Content-Type': 'application/json' },
            body: JSON.stringify({
                id: Date.now(),
                jsonrpc: '2.0',
                method: 'call',
                params: {
                    product_template_id: templateId,
                    product_id: variantId,
                    quantity: 1,
                    product_custom_attribute_values: [],
                },
            }),
        })
            .then(function (response) { return response.json(); })
            .then(function () {
                fetchAndOpenMiniCart();
                setTimeout(function () {
                    if (button) {
                        button.disabled = false;
                        button.innerHTML = button.dataset.chOriginalHtml;
                    }
                }, 2000);
            })
            .catch(function () {
                if (button) {
                    button.disabled = false;
                    button.innerHTML = button.dataset.chOriginalHtml;
                }
            });
    }

    /**
     * CH-156 — Mini-panier (panneau latéral). Squelette statique dans
     * templates/layout.xml (.ch-minicart-panel / .ch-minicart-overlay),
     * peuplé ici à partir de /capsule-house/cart-data.json (route
     * custom, voir main.py : aucune route JSON-RPC native n'existe pour
     * juste LIRE le panier, seulement pour le modifier — /shop/cart
     * natif est type='http' et rend une page HTML complète).
     * S'ouvre : après un ajout réussi (hero, ou add_to_cart_event
     * natif déclenché par website_sale sur tout autre bouton d'ajout),
     * ou via un clic sur l'icône panier du header natif.
     * +/- et suppression appellent /shop/cart/update (JSON-RPC natif,
     * même route que le panier natif utilise) et ne rafraîchissent que
     * le panneau, jamais toute la page.
     */
    function getMiniCartEls() {
        return {
            overlay: document.querySelector('[data-ch-minicart-overlay]'),
            panel: document.querySelector('[data-ch-minicart-panel]'),
            linesEl: document.querySelector('[data-ch-minicart-lines]'),
            subtotalEl: document.querySelector('[data-ch-minicart-subtotal]'),
            emptyEl: document.querySelector('[data-ch-minicart-empty]'),
        };
    }

    function openMiniCartPanel() {
        var els = getMiniCartEls();
        if (!els.panel || !els.overlay) return;
        els.overlay.classList.remove('d-none');
        els.panel.classList.remove('d-none');
        // Forcer un reflow avant d'ajouter la classe d'ouverture, pour
        // que la transition CSS (transform/opacity) se joue bien au
        // lieu de sauter directement à l'état final.
        void els.panel.offsetWidth;
        els.overlay.classList.add('ch-minicart-open');
        els.panel.classList.add('ch-minicart-open');
        els.panel.setAttribute('aria-hidden', 'false');
        document.body.classList.add('ch-minicart-locked');
    }

    function closeMiniCartPanel() {
        var els = getMiniCartEls();
        if (!els.panel || !els.overlay) return;
        els.overlay.classList.remove('ch-minicart-open');
        els.panel.classList.remove('ch-minicart-open');
        els.panel.setAttribute('aria-hidden', 'true');
        document.body.classList.remove('ch-minicart-locked');
        setTimeout(function () {
            els.overlay.classList.add('d-none');
            els.panel.classList.add('d-none');
        }, 300);
    }

    function renderMiniCart(data) {
        var els = getMiniCartEls();
        if (!els.linesEl) return;
        els.linesEl.innerHTML = '';

        var lines = data.lines || [];
        if (!lines.length) {
            if (els.emptyEl) els.emptyEl.classList.remove('d-none');
        } else {
            if (els.emptyEl) els.emptyEl.classList.add('d-none');
        }

        lines.forEach(function (line) {
            var lineEl = document.createElement('div');
            lineEl.className = 'ch-minicart-line';
            lineEl.dataset.lineId = line.line_id;

            var imgWrap = document.createElement('div');
            imgWrap.className = 'ch-minicart-line-img';
            var img = document.createElement('img');
            img.src = line.image_url;
            img.alt = line.name;
            imgWrap.appendChild(img);
            lineEl.appendChild(imgWrap);

            var body = document.createElement('div');
            body.className = 'ch-minicart-line-body';

            var nameEl = document.createElement('span');
            nameEl.className = 'ch-minicart-line-name';
            nameEl.textContent = line.name;
            body.appendChild(nameEl);

            var priceEl = document.createElement('span');
            priceEl.className = 'ch-minicart-line-price';
            priceEl.textContent = line.price_formatted;
            body.appendChild(priceEl);

            var controls = document.createElement('div');
            controls.className = 'ch-minicart-line-controls';

            var qtyWrap = document.createElement('div');
            qtyWrap.className = 'ch-minicart-qty';

            var minusBtn = document.createElement('button');
            minusBtn.type = 'button';
            minusBtn.innerHTML = '<i class="fa fa-minus"/>';
            minusBtn.addEventListener('click', function () {
                updateMiniCartLine(line.line_id, line.product_id, line.quantity - 1);
            });
            qtyWrap.appendChild(minusBtn);

            var qtySpan = document.createElement('span');
            qtySpan.textContent = line.quantity;
            qtyWrap.appendChild(qtySpan);

            var plusBtn = document.createElement('button');
            plusBtn.type = 'button';
            plusBtn.innerHTML = '<i class="fa fa-plus"/>';
            plusBtn.addEventListener('click', function () {
                updateMiniCartLine(line.line_id, line.product_id, line.quantity + 1);
            });
            qtyWrap.appendChild(plusBtn);

            controls.appendChild(qtyWrap);

            var deleteBtn = document.createElement('button');
            deleteBtn.type = 'button';
            deleteBtn.className = 'ch-minicart-line-delete';
            deleteBtn.innerHTML = '<i class="fa fa-trash"/>';
            deleteBtn.addEventListener('click', function () {
                updateMiniCartLine(line.line_id, line.product_id, 0);
            });
            controls.appendChild(deleteBtn);

            body.appendChild(controls);
            lineEl.appendChild(body);
            els.linesEl.appendChild(lineEl);
        });

        if (els.subtotalEl) {
            els.subtotalEl.textContent = data.amount_total_formatted || '';
        }

        var badges = document.querySelectorAll('.my_cart_quantity');
        badges.forEach(function (badge) {
            badge.textContent = data.cart_quantity || 0;
            if (data.cart_quantity) {
                badge.classList.remove('d-none');
            }
        });
    }

    function fetchAndRenderMiniCart() {
        return fetch('/capsule-house/cart-data.json', { headers: { 'Accept': 'application/json' } })
            .then(function (response) { return response.json(); })
            .then(function (data) {
                renderMiniCart(data);
                return data;
            });
    }

    function fetchAndOpenMiniCart() {
        fetchAndRenderMiniCart().then(function () {
            openMiniCartPanel();
        });
    }

    function updateMiniCartLine(lineId, productId, quantity) {
        fetch('/shop/cart/update', {
            method: 'POST',
            headers: { 'Content-Type': 'application/json' },
            body: JSON.stringify({
                id: Date.now(),
                jsonrpc: '2.0',
                method: 'call',
                params: {
                    line_id: lineId,
                    product_id: productId,
                    quantity: Math.max(0, quantity),
                },
            }),
        })
            .then(function () {
                fetchAndRenderMiniCart();
            })
            .catch(function () {
                // Silencieux : dégradation gracieuse, cohérent avec le
                // reste de ce fichier.
            });
    }

    function initMiniCart() {
        var els = getMiniCartEls();
        if (!els.panel || !els.overlay) return;

        var closeBtn = document.querySelector('[data-ch-minicart-close]');
        if (closeBtn && !closeBtn.dataset.chBound) {
            closeBtn.dataset.chBound = '1';
            closeBtn.addEventListener('click', closeMiniCartPanel);
        }

        if (!els.overlay.dataset.chBound) {
            els.overlay.dataset.chBound = '1';
            els.overlay.addEventListener('click', closeMiniCartPanel);
        }

        // Icône panier du header natif Odoo : on intercepte son clic
        // pour ouvrir notre panneau au lieu de naviguer directement
        // vers /shop/cart (l'utilisateur peut toujours y aller via le
        // bouton "Aller au panier" du panneau, ou en cliquant deux
        // fois si jamais il préfère la page complète).
        var cartIcon = document.querySelector('li.o_wsale_my_cart a, .o_wsale_my_cart');
        if (cartIcon && !cartIcon.dataset.chBound) {
            cartIcon.dataset.chBound = '1';
            cartIcon.addEventListener('click', function (ev) {
                ev.preventDefault();
                fetchAndOpenMiniCart();
            });
        }

        // Déclenché par website_sale (cart_service.js) à chaque ajout
        // réussi, peu importe le bouton d'origine (fiche produit,
        // carousel Meilleures ventes) — voir _trackProducts() côté
        // natif. On l'utilise ici comme simple signal ("un ajout vient
        // d'avoir lieu"), pas pour son contenu (tracking_info, pas les
        // lignes du panier).
        var saleRoot = document.querySelector('.oe_website_sale');
        if (saleRoot && !saleRoot.dataset.chMinicartBound) {
            saleRoot.dataset.chMinicartBound = '1';
            saleRoot.addEventListener('add_to_cart_event', function () {
                fetchAndOpenMiniCart();
            });
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

        if (data.cart_product_id && data.cart_variant_id) {
            var cartButton = hero.querySelector('[data-ch-cart-shortcut]');
            if (cartButton && !cartButton.dataset.chBound) {
                cartButton.dataset.chBound = '1';
                cartButton.addEventListener('click', function () {
                    addToCartJsonRpc(data.cart_product_id, data.cart_variant_id, cartButton);
                });
            }
            if (cartButton) {
                cartButton.classList.remove('d-none');
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
        initFeaturedProductsCarousel();
        initHeroDynamicContent();
        initTestimonialsSection();
        initPaymentMethodsSection();
        initMiniCart();
    }

    if (document.readyState === 'loading') {
        document.addEventListener('DOMContentLoaded', init);
    } else {
        init();
    }
    document.addEventListener('page:loaded', init);
})();
