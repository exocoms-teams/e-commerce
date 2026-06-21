(function () {
    'use strict';

    const dropdowns = document.querySelectorAll('.exo-dropdown');
    const burger = document.querySelector('.exo-burger');
    const nav = document.querySelector('.exo-nav');

    function initDropdowns() {
        if (!dropdowns.length) return;
        let timeout;
        dropdowns.forEach(dropdown => {
            const button = dropdown.querySelector('.exo-dropdown-btn');
            if (!button) return;
            dropdown.addEventListener('mouseenter', () => { clearTimeout(timeout); dropdown.classList.add('active'); });
            dropdown.addEventListener('mouseleave', () => { timeout = setTimeout(() => dropdown.classList.remove('active'), 300); });
            button.addEventListener('click', (e) => { e.preventDefault(); dropdown.classList.toggle('active'); });
        });
    }

    function initBurgerMenu() {
        if (!burger || !nav) return;
        burger.addEventListener('click', () => {
            burger.classList.toggle('active');
            nav.classList.toggle('active');
            document.body.style.overflow = nav.classList.contains('active') ? 'hidden' : '';
        });
    }

    function initScrollReveal() {
        if (!('IntersectionObserver' in window)) return;
        const targets = document.querySelectorAll('.mq-sol-card, .mq-hp-prod-card, [data-animate]');
        const observer = new IntersectionObserver((entries) => {
            entries.forEach(entry => {
                if (entry.isIntersecting) {
                    entry.target.style.opacity = '1';
                    entry.target.style.transform = 'translateY(0)';
                    const animation = entry.target.dataset.animate;
                    if (animation) entry.target.classList.add(`animate-${animation}`);
                    observer.unobserve(entry.target);
                }
            });
        }, { threshold: 0.1 });
        targets.forEach((el, i) => {
            el.style.opacity = '0';
            el.style.transform = 'translateY(14px)';
            el.style.transition = `opacity 0.45s ease ${i * 0.06}s, transform 0.45s ease ${i * 0.06}s`;
            observer.observe(el);
        });
    }

    function initPriceFilter() {
        // On ne fait rien si on n'est pas sur une page shop
        const shopHeader = document.querySelector('.o_wsale_products_header_search_form_container');
        if (!shopHeader) return;

        // Le filtre prix est dans la sidebar native #products_grid_before
        // On cherche dans TOUT le document
        const priceFilter = document.querySelector('.o_wsale_products_price_filter');
        if (!priceFilter) return;

        // Conteneur cible = la div qui contient search + sort by
        const headerRow = shopHeader.closest('div') || shopHeader.parentElement;
        if (!headerRow) return;

        // Déplace le filtre prix après la recherche, avant Sort By
        const sortEl = headerRow.querySelector('.o_wsale_products_sort')
                    || headerRow.querySelector('[name="order"]');

        if (sortEl) {
            headerRow.insertBefore(priceFilter, sortEl);
        } else {
            headerRow.appendChild(priceFilter);
        }

        // Ouvre l'accordion
        const collapse = priceFilter.querySelector('.accordion-collapse');
        if (collapse) {
            collapse.classList.add('show');
            collapse.style.display = 'block';
        }

        // Cache le titre "Price Range"
        const accordionHeader = priceFilter.querySelector('.accordion-header');
        if (accordionHeader) accordionHeader.style.display = 'none';

        priceFilter.style.display = 'flex';
        priceFilter.style.alignItems = 'center';
        priceFilter.style.minWidth = '180px';
    }

    /* ═══════════════════════════════════════════════════════════
       HEADER — dropdown profil, burger menu mobile.
       La recherche utilise désormais le modal natif Bootstrap
       #o_search_modal (data-bs-toggle="modal"), géré entièrement
       par Odoo — plus besoin de JS personnalisé pour l'ouverture/
       fermeture, le clic extérieur ou la touche Escape.
       ═══════════════════════════════════════════════════════════ */

    function initHeaderProfileDropdown() {
        var profileDropdown = document.querySelector('.exo-profile-dropdown');
        if (profileDropdown) {
            var profileTimeout;
            profileDropdown.addEventListener('mouseenter', function() {
                clearTimeout(profileTimeout);
                profileDropdown.classList.add('active');
            });
            profileDropdown.addEventListener('mouseleave', function() {
                profileTimeout = setTimeout(function() {
                    profileDropdown.classList.remove('active');
                }, 300);
            });
        }
    }

    function initHeaderBurgerMenu() {
        var headerBurger    = document.getElementById('exo-burger');
        var headerMobileNav = document.getElementById('exo-mobile-nav');

        if (headerBurger && headerMobileNav) {
            headerBurger.addEventListener('click', function() {
                var isOpen = headerMobileNav.classList.toggle('open');
                headerBurger.classList.toggle('active');
                headerBurger.setAttribute('aria-expanded', isOpen ? 'true' : 'false');
                headerMobileNav.setAttribute('aria-hidden', isOpen ? 'false' : 'true');
                document.body.style.overflow = isOpen ? 'hidden' : '';
            });

            /* Ferme le menu mobile au clic sur un lien */
            headerMobileNav.querySelectorAll('.exo-mobile-link').forEach(function(link) {
                link.addEventListener('click', function() {
                    headerMobileNav.classList.remove('open');
                    headerBurger.classList.remove('active');
                    headerBurger.setAttribute('aria-expanded', 'false');
                    headerMobileNav.setAttribute('aria-hidden', 'true');
                    document.body.style.overflow = '';
                });
            });
        }
    }

    function init() {
        initDropdowns();
        initBurgerMenu();
        initScrollReveal();
        initPriceFilter();
        initHeaderProfileDropdown();
        initHeaderBurgerMenu();
    }

    if (document.readyState === 'loading') {
        document.addEventListener('DOMContentLoaded', init);
    } else {
        init();
    }
})();