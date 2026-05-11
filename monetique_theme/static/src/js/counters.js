/** @odoo-module **/

/**
 * monetiques.fr Counters — animated number counters for stats sections.
 *
 * Usage in XML templates:
 *   <span class="pc-stat__number"
 *         data-animate="counter"
 *         data-target="10000"
 *         data-suffix="+"
 *         data-prefix=""
 *         data-duration="1800">
 *     0
 *   </span>
 *
 * Attributes:
 *   data-target    {number}  Final value to count up to (required)
 *   data-suffix    {string}  Text appended after number, e.g. "+" or "%" (optional)
 *   data-prefix    {string}  Text prepended before number, e.g. "€" (optional)
 *   data-duration  {number}  Animation duration in ms (default: 1600)
 *   data-decimals  {number}  Decimal places to display (default: 0)
 *
 * Counters only start once .is-visible is added by animations.js.
 * Uses a MutationObserver to detect that class addition.
 */

export const paycoreCounters = {
    /**
     * MutationObserver watching for .is-visible additions.
     * @type {MutationObserver|null}
     */
    _mutationObserver: null,

    /**
     * Easing function — ease out cubic.
     * @param {number} t  Progress [0, 1]
     * @returns {number}
     */
    _easeOutCubic(t) {
        return 1 - Math.pow(1 - t, 3);
    },

    /**
     * Easing function — ease out quart (slightly more dramatic).
     * @param {number} t  Progress [0, 1]
     * @returns {number}
     */
    _easeOutQuart(t) {
        return 1 - Math.pow(1 - t, 4);
    },

    /**
     * Format a number for display.
     * Adds locale-appropriate thousands separators.
     * @param {number} value
     * @param {number} decimals
     * @returns {string}
     */
    _formatNumber(value, decimals = 0) {
        return value.toLocaleString("fr-FR", {
            minimumFractionDigits: decimals,
            maximumFractionDigits: decimals,
        });
    },

    /**
     * Animate a single counter element.
     * @param {HTMLElement} el
     */
    _animateCounter(el) {
        if (el.dataset.counted) return; // Prevent double-animation
        el.dataset.counted = "true";

        const target = parseFloat(el.dataset.target || "0");
        const duration = parseInt(el.dataset.duration || "1600", 10);
        const decimals = parseInt(el.dataset.decimals || "0", 10);
        const suffix = el.dataset.suffix || "";
        const prefix = el.dataset.prefix || "";

        // Respect prefers-reduced-motion
        if (window.matchMedia("(prefers-reduced-motion: reduce)").matches) {
            el.textContent = prefix + this._formatNumber(target, decimals) + suffix;
            return;
        }

        const startTime = performance.now();
        const startValue = 0;

        const update = (currentTime) => {
            const elapsed = currentTime - startTime;
            const progress = Math.min(elapsed / duration, 1);
            const easedProgress = this._easeOutQuart(progress);
            const currentValue = startValue + (target - startValue) * easedProgress;

            el.textContent = prefix + this._formatNumber(currentValue, decimals) + suffix;

            if (progress < 1) {
                requestAnimationFrame(update);
            } else {
                // Ensure we land exactly on target
                el.textContent = prefix + this._formatNumber(target, decimals) + suffix;
            }
        };

        requestAnimationFrame(update);
    },

    /**
     * Initialize the counters system.
     * Watches for [data-animate="counter"] elements becoming visible.
     */
    init() {
        const counterElements = document.querySelectorAll(
            '[data-animate="counter"]'
        );

        if (!counterElements.length) return;

        // Watch for .is-visible being added to counter elements
        this._mutationObserver = new MutationObserver((mutations) => {
            mutations.forEach((mutation) => {
                if (
                    mutation.type === "attributes" &&
                    mutation.attributeName === "class"
                ) {
                    const el = mutation.target;
                    if (
                        el.classList.contains("is-visible") &&
                        el.dataset.animate === "counter"
                    ) {
                        this._animateCounter(el);
                    }
                }
            });
        });

        counterElements.forEach((el) => {
            this._mutationObserver.observe(el, {
                attributes: true,
                attributeFilter: ["class"],
            });

            // If the element is already visible on init (e.g., above the fold)
            if (el.classList.contains("is-visible")) {
                this._animateCounter(el);
            }
        });
    },

    /**
     * Re-scan for new counter elements (after dynamic content injection).
     */
    refresh() {
        const newCounters = document.querySelectorAll(
            '[data-animate="counter"]:not([data-counted])'
        );

        newCounters.forEach((el) => {
            if (this._mutationObserver) {
                this._mutationObserver.observe(el, {
                    attributes: true,
                    attributeFilter: ["class"],
                });
            }

            if (el.classList.contains("is-visible")) {
                this._animateCounter(el);
            }
        });
    },

    /**
     * Tear down. Called on page unload.
     */
    destroy() {
        if (this._mutationObserver) {
            this._mutationObserver.disconnect();
            this._mutationObserver = null;
        }
    },
};
