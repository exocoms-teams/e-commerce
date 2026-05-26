(function () {
    'use strict';

    // --- SÉLECTEURS ---
    const dropdowns = document.querySelectorAll('.exo-dropdown');
    const burger = document.querySelector('.exo-burger');
    const nav = document.querySelector('.exo-nav');
    const header = document.querySelector('.exo-header');

    // --- DROPDOWNS ---
    function initDropdowns() {
        if (!dropdowns.length) return;
        let timeout;
        dropdowns.forEach(dropdown => {
            const button = dropdown.querySelector('.exo-dropdown-btn');
            if (!button) return;
            dropdown.addEventListener('mouseenter', () => {
                clearTimeout(timeout);
                dropdown.classList.add('active');
            });
            dropdown.addEventListener('mouseleave', () => {
                timeout = setTimeout(() => dropdown.classList.remove('active'), 300);
            });
            button.addEventListener('click', (e) => {
                e.preventDefault();
                dropdown.classList.toggle('active');
            });
        });
    }

    // --- BURGER MENU ---
    function initBurgerMenu() {
        if (!burger || !nav) return;
        burger.addEventListener('click', () => {
            burger.classList.toggle('active');
            nav.classList.toggle('active');
            document.body.style.overflow = nav.classList.contains('active') ? 'hidden' : '';
        });
    }

    // --- SCROLL REVEAL ---
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

    // --- FILTRE PRIX — déplacement dans la barre header shop ---
    function initPriceFilter() {
        // On ne fait rien si on n'est pas sur une page shop
        const shopHeader = document.getElementById('o_wsale_products_header');
        if (!shopHeader) return;

        // Le filtre prix est rendu dans la sidebar par Odoo
        // On le déplace dans le header entre la recherche et Sort By
        const priceFilter = document.querySelector('.o_wsale_products_price_filter');
        const sortBy = shopHeader.querySelector('.o_wsale_products_sort, [name="order"]')
                    || shopHeader.lastElementChild;

        if (!priceFilter) return;

        // Déplace le filtre dans le header avant le Sort By
        shopHeader.insertBefore(priceFilter, sortBy);

        // Ouvre l'accordion du filtre prix automatiquement
        const collapseEl = priceFilter.querySelector('.accordion-collapse');
        if (collapseEl) {
            collapseEl.classList.add('show');
            collapseEl.style.display = 'block';
        }

        // Cache le titre "Price Range" — on garde juste le slider
        const accordionHeader = priceFilter.querySelector('.accordion-header');
        if (accordionHeader) accordionHeader.style.display = 'none';

        // Style inline pour l'alignement
        priceFilter.style.display = 'flex';
        priceFilter.style.alignItems = 'center';
        priceFilter.style.gap = '8px';
        priceFilter.style.minWidth = '200px';
        priceFilter.style.flexShrink = '0';
    }

    // --- INITIALISATION GÉNÉRALE ---
    function init() {
        initDropdowns();
        initBurgerMenu();
        initScrollReveal();
        initPriceFilter();
    }

    if (document.readyState === 'loading') {
        document.addEventListener('DOMContentLoaded', init);
    } else {
        init();
    }
})();