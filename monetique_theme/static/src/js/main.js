/** @odoo-module **/
/**
 * PayCore — main.js
 * Point d'entrée JS principal. Import des modules.
 * Utilise le système de modules Odoo 17+/19.
 */

import { paycoreNavbar } from './navbar';
import { paycoreAnimations } from './animations';
import { paycoreCounters } from './counters';

// Initialisation au DOM ready
document.addEventListener('DOMContentLoaded', () => {
    paycoreNavbar.init();
    paycoreAnimations.init();
    paycoreCounters.init();

    // Année dynamique dans le footer
    const yearEl = document.getElementById('pc-year');
    if (yearEl) yearEl.textContent = new Date().getFullYear();
});
