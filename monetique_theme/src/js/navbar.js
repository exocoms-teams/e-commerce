/** @odoo-module **/
/**
 * monetiques.fr — navbar.js
 * Gestion de la navbar : sticky scroll, menu mobile, dropdowns accessibles.
 */

export const paycoreNavbar = {

    navbar: null,
    burger: null,
    mobileMenu: null,
    isMenuOpen: false,
    lastScrollY: 0,


    init() {
        this.navbar = document.getElementById('pc-navbar');
        this.burger = document.getElementById('pc-burger');
        this.mobileMenu = document.getElementById('pc-mobile-menu');

        if (!this.navbar) return;

        this._bindScroll();
        this._bindBurger();
        this._bindDropdowns();
        this._bindEscape();
        this._bindOutsideClick();
        this._setActiveLink();
    },


    // -------------------------------------------------------------------------
    // Scroll sticky
    // -------------------------------------------------------------------------

    _bindScroll() {
        const threshold = 20;

        const onScroll = () => {
            const scrollY = window.scrollY;

            if (scrollY > threshold) {
                this.navbar.classList.add('is-scrolled');
            } else {
                this.navbar.classList.remove('is-scrolled');
            }

            this.lastScrollY = scrollY;
        };

        window.addEventListener('scroll', onScroll, { passive: true });
        onScroll(); // état initial
    },


    // -------------------------------------------------------------------------
    // Menu mobile burger
    // -------------------------------------------------------------------------

    _bindBurger() {
        if (!this.burger || !this.mobileMenu) return;

        this.burger.addEventListener('click', () => {
            this.isMenuOpen ? this._closeMobileMenu() : this._openMobileMenu();
        });
    },

    _openMobileMenu() {
        this.isMenuOpen = true;
        this.burger.setAttribute('aria-expanded', 'true');
        this.mobileMenu.setAttribute('aria-hidden', 'false');
        this.mobileMenu.classList.add('is-open');
        document.body.style.overflow = 'hidden';
    },

    _closeMobileMenu() {
        this.isMenuOpen = false;
        this.burger.setAttribute('aria-expanded', 'false');
        this.mobileMenu.setAttribute('aria-hidden', 'true');
        this.mobileMenu.classList.remove('is-open');
        document.body.style.overflow = '';
    },


    // -------------------------------------------------------------------------
    // Dropdowns desktop (accessibilité ARIA)
    // -------------------------------------------------------------------------

    _bindDropdowns() {
        const dropdownTriggers = this.navbar.querySelectorAll('.pc-navbar__link--has-dropdown');

        dropdownTriggers.forEach(trigger => {
            const parent = trigger.closest('.pc-navbar__item--dropdown');

            // Keyboard support
            trigger.addEventListener('keydown', (e) => {
                if (e.key === 'Enter' || e.key === ' ') {
                    e.preventDefault();
                    const isExpanded = trigger.getAttribute('aria-expanded') === 'true';
                    trigger.setAttribute('aria-expanded', String(!isExpanded));
                }
            });

            // Mouse enter/leave sur le parent
            parent.addEventListener('mouseenter', () => {
                trigger.setAttribute('aria-expanded', 'true');
            });

            parent.addEventListener('mouseleave', () => {
                trigger.setAttribute('aria-expanded', 'false');
            });
        });
    },


    // -------------------------------------------------------------------------
    // Escape key : ferme tout
    // -------------------------------------------------------------------------

    _bindEscape() {
        document.addEventListener('keydown', (e) => {
            if (e.key === 'Escape') {
                if (this.isMenuOpen) this._closeMobileMenu();

                // Fermer les dropdowns
                this.navbar
                    ?.querySelectorAll('[aria-expanded="true"]')
                    .forEach(el => el.setAttribute('aria-expanded', 'false'));
            }
        });
    },


    // -------------------------------------------------------------------------
    // Clic en dehors : ferme menu mobile
    // -------------------------------------------------------------------------

    _bindOutsideClick() {
        document.addEventListener('click', (e) => {
            if (this.isMenuOpen && !this.navbar.contains(e.target)) {
                this._closeMobileMenu();
            }
        });
    },


    // -------------------------------------------------------------------------
    // Active link highlighting
    // -------------------------------------------------------------------------

    _setActiveLink() {
        const currentPath = window.location.pathname;

        this.navbar.querySelectorAll('.pc-navbar__link, .pc-navbar__dropdown-item, .pc-navbar__mobile-link').forEach(link => {
            const href = link.getAttribute('href');
            if (href && href !== '/' && currentPath.startsWith(href)) {
                link.classList.add('is-active');
                link.setAttribute('aria-current', 'page');
            } else if (href === '/' && currentPath === '/') {
                link.classList.add('is-active');
                link.setAttribute('aria-current', 'page');
            }
        });
    },
};
