/** @odoo-module **/

/**
 * PayCore Animations — IntersectionObserver-based scroll animations.
 *
 * Usage in XML templates:
 *   data-animate="fade-up"          → fade + translate-Y
 *   data-animate="fade-in"          → fade only
 *   data-animate="slide-right"      → slide from left
 *   data-animate="scale-in"         → scale from 0.92
 *   data-animate="counter"          → handled by counters.js
 *   data-delay="100"                → stagger delay in ms (optional)
 *
 * Elements receive `.is-visible` when they enter the viewport.
 * The SCSS in _animations.scss handles the actual CSS transitions.
 */

export const paycoreAnimations = {
    /**
     * IntersectionObserver instance.
     * @type {IntersectionObserver|null}
     */
    _observer: null,

    /**
     * Initialize scroll-driven animations.
     * Safe to call multiple times — disconnects any existing observer first.
     */
    init() {
        // Respect user's motion preferences
        const prefersReduced = window.matchMedia(
            "(prefers-reduced-motion: reduce)"
        ).matches;

        if (prefersReduced) {
            // Make all animated elements immediately visible
            document
                .querySelectorAll("[data-animate]")
                .forEach((el) => el.classList.add("is-visible"));
            return;
        }

        // Disconnect previous observer if re-initialising (SPA navigation)
        if (this._observer) {
            this._observer.disconnect();
        }

        this._observer = new IntersectionObserver(
            this._onIntersect.bind(this),
            {
                // Start animation slightly before element enters the viewport
                rootMargin: "-50px 0px -50px 0px",
                threshold: 0.12,
            }
        );

        // Observe every element that declares an animation type
        document
            .querySelectorAll("[data-animate]:not(.is-visible)")
            .forEach((el) => {
                this._applyInitialState(el);
                this._observer.observe(el);
            });
    },

    /**
     * Apply the "hidden" initial CSS state based on animation type.
     * This mirrors what the SCSS does but ensures elements start hidden
     * even if the stylesheet hasn't applied yet.
     * @param {HTMLElement} el
     */
    _applyInitialState(el) {
        const type = el.dataset.animate;
        const delay = parseInt(el.dataset.delay || "0", 10);

        // Apply stagger delay as a CSS custom property so SCSS can use it
        if (delay > 0) {
            el.style.transitionDelay = `${delay}ms`;
            el.style.animationDelay = `${delay}ms`;
        }

        // Only add the class that marks the element as "waiting to animate"
        // The actual visual hidden state is handled purely in SCSS
        el.classList.add("animate-pending");
    },

    /**
     * IntersectionObserver callback.
     * @param {IntersectionObserverEntry[]} entries
     */
    _onIntersect(entries) {
        entries.forEach((entry) => {
            if (!entry.isIntersecting) return;

            const el = entry.target;

            // Trigger the animation
            requestAnimationFrame(() => {
                el.classList.add("is-visible");
            });

            // Stop observing once animated — we don't replay
            this._observer.unobserve(el);
        });
    },

    /**
     * Manually trigger an element's animation (e.g., after dynamic content load).
     * @param {HTMLElement} el
     */
    triggerElement(el) {
        el.classList.add("is-visible");
    },

    /**
     * Re-scan the DOM for new [data-animate] elements.
     * Useful after Odoo's dynamic content injection.
     */
    refresh() {
        document
            .querySelectorAll("[data-animate]:not(.animate-pending):not(.is-visible)")
            .forEach((el) => {
                this._applyInitialState(el);
                if (this._observer) {
                    this._observer.observe(el);
                }
            });
    },

    /**
     * Tear down the observer. Called on page unload or module destroy.
     */
    destroy() {
        if (this._observer) {
            this._observer.disconnect();
            this._observer = null;
        }
    },
};
