(function () {
    'use strict';

    // --- SÉLECTEURS ---
    const dropdowns = document.querySelectorAll('.exo-dropdown');
    const burger = document.querySelector('.exo-burger');
    const nav = document.querySelector('.exo-nav');
    const header = document.querySelector('.exo-header');
    // Ajoute ici le sélecteur pour ta modale
    const modal = document.querySelector('.ton-selecteur-modal'); 

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

    // --- SCROLL REVEAL (Animation au défilement) ---
    function initScrollReveal() {
        if (!('IntersectionObserver' in window)) return;
        const targets = document.querySelectorAll('.mq-sol-card, .mq-hp-prod-card, [data-animate]');
        
        const observer = new IntersectionObserver((entries) => {
            entries.forEach(entry => {
                if (entry.isIntersecting) {
                    entry.target.style.opacity = '1';
                    entry.target.style.transform = 'translateY(0)';
                    // Si tu utilises data-animate
                    const animation = entry.target.dataset.animate;
                    if(animation) entry.target.classList.add(`animate-${animation}`);
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

    // --- INITIALISATION GÉNÉRALE ---
    function init() {
        initDropdowns();
        initBurgerMenu();
        initScrollReveal();
        // Ajoute ici tes autres appels (SmoothScroll, Cart, etc.)
    }

    if (document.readyState === 'loading') {
        document.addEventListener('DOMContentLoaded', init);
    } else {
        init();
    }
})();