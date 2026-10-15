/** @odoo-module **/

import publicWidget from "@web/legacy/js/public/public_widget";

// Cibles precises : textes, images, cartes et blocs visuels autonomes.
// Les composants d'un meme groupe sont cibles au meme niveau pour eviter
// qu'un seul bloc frere recoive le reveal ; les descendants sont dedupliques.
const TARGET_SELECTORS = [
    '#wrapwrap main h1',
    '#wrapwrap main h2',
    '#wrapwrap main h3',
    '#wrapwrap main p',
    '#wrapwrap main .ch-btn',
    '#wrapwrap main .accordion-button',
    '#wrapwrap main img:not(.ch-hero-illustration):not([fetchpriority="high"])',
    '.ch-rating-badge',
    '.ch-hero-btn-action',
    '.ch-hero-div-note',
    '.ch-trust-row',
    '.ch-product-card',
    '#products_grid .o_wsale_product_grid_wrapper',
    '.ch-gamme-card',
    '.ch-usage-card',
    '.ch-models-empty',
    '.ch-testi-card',
    '.ch-avis-card',
    '.ch-avis-form-card',
    '.ch-aide-card',
    '.ch-aide-faq-category',
    '.ch-aide-faq .accordion',
    '.ch-aide-timeline-item',
    '.ch-aide-steps-item',
    '.ch-aide-warranty',
    '.ch-aide-callout',
    '.ch-aide-table tbody > tr',
    '.ch-gamme-perf-card',
    '.ch-gamme-format-card',
    '.ch-gamme-equip-item',
    '.ch-entreprise-stat',
    '.ch-entreprise-history-item',
    '.ch-entreprise-diagram-visual svg',
    '.ch-entreprise-diagram-legend',
    '.ch-entreprise-compare tbody > tr',
    '.ch-avis-score-block',
    '.ch-avis-bars-block',
    '.ch-contact-form-intro',
    '.ch-contact-reassurance',
    '.ch-contact-info-card',
    '.ch-devis-content',
];

const TARGET_SELECTOR = TARGET_SELECTORS.join(', ');

// Grilles dont les cartes gardent une petite cascade au scroll.
const GRID_SELECTORS = [
    '.ch-bestsellers-track',
    '#products_grid',
    '.ch-gammes-home',
    '.ch-usages-zone',
    '.ch-avis-grid',
    '[data-ch-testimonials-grid]',
    '.ch-aide-cards',
    '.ch-aide-timeline',
    '.ch-gamme-perf-grid',
    '.ch-gamme-formats-grid',
    '.ch-gamme-equip-grid',
    '.ch-entreprise-stats',
    '.ch-entreprise-history',
];

let initialScanDone = false;
let restoredFromBfcache = false;
let pageShowListenerBound = false;

function releaseEarlyRevealFlag() {
    if (window.__capsuleHouseRevealSafetyTimeout != null) {
        window.clearTimeout(window.__capsuleHouseRevealSafetyTimeout);
        window.__capsuleHouseRevealSafetyTimeout = null;
    }
    document.documentElement.classList.remove('js-reveal');
}

function bindPageShowListener() {
    if (pageShowListenerBound) {
        return;
    }
    pageShowListenerBound = true;

    // La page peut etre restauree sans recharger ses scripts depuis le cache.
    // On retire alors les classes d'intro encore presentes pour ne pas la rejouer.
    window.addEventListener('pageshow', (event) => {
        if (!event.persisted) {
            return;
        }
        restoredFromBfcache = true;
        releaseEarlyRevealFlag();
        document.querySelectorAll('#wrapwrap .reveal-intro').forEach((target) => {
            target.classList.remove('reveal-intro');
            target.style.removeProperty('--delay');
        });
    });
}

function isBackForwardNavigation() {
    if (!window.performance || typeof window.performance.getEntriesByType !== 'function') {
        return false;
    }
    const navigation = window.performance.getEntriesByType('navigation')[0];
    return navigation && navigation.type === 'back_forward';
}

publicWidget.registry.CapsuleHouseScrollReveal = publicWidget.Widget.extend({
    selector: '#wrapwrap',
    disabledInEditableMode: true,

    start: function () {
        const result = this._super.apply(this, arguments);
        const reducedMotion = window.matchMedia &&
            window.matchMedia('(prefers-reduced-motion: reduce)').matches;

        // Odoo 19 transmet le mode d'edition au widget dans options.editableMode.
        // Les classes du body restent des gardes supplementaires pour les vues
        // d'edition qui n'auraient pas encore recu cette option.
        const editableMode = this.options && this.options.editableMode === true;
        const body = document.body;
        const bodyIsEditable = body && (
            body.classList.contains('editor_enable') ||
            body.classList.contains('o_is_editable')
        );
        if (reducedMotion || editableMode || bodyIsEditable) {
            releaseEarlyRevealFlag();
            return result;
        }
        bindPageShowListener();

        if ('IntersectionObserver' in window) {
            this._revealObserver = new IntersectionObserver((entries) => {
                entries.forEach((entry) => {
                    if (!entry.isIntersecting) {
                        return;
                    }
                    entry.target.classList.add('is-visible');
                    this._revealObserver.unobserve(entry.target);
                });
            }, {
                threshold: 0.15,
                rootMargin: '0px 0px -40px 0px',
            });
        }

        const initialize = () => {
            if (this.isDestroyed()) {
                releaseEarlyRevealFlag();
                return;
            }
            if (initialScanDone) {
                // Un redemarrage du widget ne rejoue jamais l'intro initiale.
                this._scanForScrollReveal(this.el);
            } else {
                initialScanDone = true;
                const introAllowed = !restoredFromBfcache &&
                    !isBackForwardNavigation() &&
                    window.__capsuleHouseRevealTimedOut !== true &&
                    window.scrollY <= 0 &&
                    !window.location.hash;
                this._scanInitialTargets(this.el, introAllowed);
            }
            // Le CSS a pris le relais sans laisser le navigateur peindre entre
            // l'ajout des classes reveal et le retrait du drapeau initial.
            releaseEarlyRevealFlag();
            this._observeContentChanges();
        };

        // Le widget Odoo demarre normalement apres DOMContentLoaded. Cette
        // garde conserve le bon ordre si le demarrage arrive plus tot.
        if (document.readyState === 'loading') {
            this._domReadyHandler = initialize;
            document.addEventListener('DOMContentLoaded', this._domReadyHandler, { once: true });
        } else {
            initialize();
        }

        return result;
    },

    _observeContentChanges: function () {
        if (!('MutationObserver' in window) || this._contentObserver) {
            return;
        }
        this._contentObserver = new MutationObserver((mutations) => {
            mutations.forEach((mutation) => {
                mutation.addedNodes.forEach((node) => {
                    if (node.nodeType === Node.ELEMENT_NODE) {
                        this._scanForScrollReveal(node);
                    }
                });
            });
        });
        this._contentObserver.observe(this.el, {
            childList: true,
            subtree: true,
        });
    },

    _getTargets: function (root) {
        const targets = [];
        if (root.matches && root.matches(TARGET_SELECTOR)) {
            targets.push(root);
        }
        root.querySelectorAll(TARGET_SELECTOR).forEach((target) => targets.push(target));

        // Les selecteurs peuvent viser un bloc et ses descendants. On ne garde
        // que la cible la plus precise deja retenue, pour eviter les doubles effets.
        return targets.filter((target) => {
            // Une cible englobante ne doit pas masquer une image prioritaire
            // ou l'illustration principale du hero pendant son chargement.
            if (target.querySelector('img[fetchpriority="high"], img.ch-hero-illustration')) {
                return false;
            }

            let ancestor = target.parentElement;
            while (ancestor && ancestor !== this.el.parentElement) {
                if (ancestor.matches(TARGET_SELECTOR)) {
                    return false;
                }
                ancestor = ancestor.parentElement;
            }
            return true;
        });
    },

    _scanInitialTargets: function (root, introAllowed) {
        let introIndex = 0;
        this._getTargets(root).forEach((target) => {
            if (this._isExcluded(target)) {
                return;
            }

            const bounds = target.getBoundingClientRect();
            const isInViewport = bounds.height > 0 && bounds.width > 0 &&
                bounds.top < window.innerHeight && bounds.bottom > 0 &&
                bounds.left < window.innerWidth && bounds.right > 0;

            if (isInViewport) {
                if (introAllowed) {
                    target.style.setProperty('--delay', `${Math.min(introIndex * 100, 600)}ms`);
                    target.classList.add('reveal-intro');
                    introIndex += 1;
                }
                // Sur une ancre ou une restauration de scroll, le contenu deja
                // visible reste immediatement affiche, sans classe d'intro.
                return;
            }

            this._prepareScrollTarget(target);
        });
    },

    _scanForScrollReveal: function (root) {
        this._getTargets(root).forEach((target) => {
            if (!this._isExcluded(target)) {
                this._prepareScrollTarget(target);
            }
        });
    },

    _isExcluded: function (target) {
        if (target.closest('[data-no-reveal]') ||
            target.closest('header, nav, footer, [role="navigation"]') ||
            target.closest('.ch-aide-sidebar, .ch-entreprise-nav')) {
            return true;
        }

        // Un enfant d'un conteneur fixe ou sticky ne doit pas etre anime non plus.
        let current = target;
        while (current && current !== this.el.parentElement) {
            const position = window.getComputedStyle(current).position;
            if (position === 'fixed' || position === 'sticky') {
                return true;
            }
            current = current.parentElement;
        }
        return false;
    },

    _prepareScrollTarget: function (target) {
        if (target.classList.contains('reveal') ||
            target.classList.contains('reveal-intro') ||
            target.closest('.reveal, .reveal-intro')) {
            return;
        }

        target.classList.add('reveal');
        this._setScrollDelay(target);

        if (this._revealObserver) {
            this._revealObserver.observe(target);
        } else {
            // Sans IntersectionObserver, aucun bloc ne reste masque.
            target.classList.add('is-visible');
        }
    },

    _setScrollDelay: function (target) {
        const gridSelector = GRID_SELECTORS.join(', ');
        const grid = target.closest(gridSelector);
        if (!grid) {
            target.style.setProperty('--delay', '0ms');
            return;
        }

        const siblings = this._getTargets(grid).filter((item) =>
            item.closest(gridSelector) === grid
        );
        const index = siblings.indexOf(target);
        target.style.setProperty('--delay', `${(Math.max(index, 0) % 4) * 120}ms`);
    },

    destroy: function () {
        if (this._domReadyHandler) {
            document.removeEventListener('DOMContentLoaded', this._domReadyHandler);
        }
        if (this._revealObserver) {
            this._revealObserver.disconnect();
        }
        if (this._contentObserver) {
            this._contentObserver.disconnect();
        }
        return this._super.apply(this, arguments);
    },
});
