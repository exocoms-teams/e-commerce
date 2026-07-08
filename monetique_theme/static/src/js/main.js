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
        const targets = document.querySelectorAll(
            '.mq-sol-card, .mq-hp-prod-card, .exo-vendor-card, .exo-category-card, .exo-testimonial-card, [data-animate]'
        );
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

    function initHeaderScrollEffect() {
        const header = document.querySelector('header.o_header_standard, .o_header_sticky, header#top');
        if (!header) return;
        const onScroll = () => {
            header.classList.toggle('exo-scrolled', window.scrollY > 12);
        };
        onScroll();
        window.addEventListener('scroll', onScroll, { passive: true });
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

    function init() {
        initDropdowns();
        initBurgerMenu();
        initScrollReveal();
        initHeaderScrollEffect();
        initPriceFilter();
    }

    if (document.readyState === 'loading') {
        document.addEventListener('DOMContentLoaded', init);
    } else {
        init();
    }
})();