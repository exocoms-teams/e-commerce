/** @odoo-module **/
/* static/src/js/coming_soon_toast.js
   WIN-123 : boutons d'action visuellement presents mais non fonctionnels
   sur les pages "coquilles" (ex: "+ Nouvelle collection"). Au clic,
   affiche un toast "Bientot disponible" au lieu de ne rien faire -
   pas de veritable logique metier, juste un retour visuel honnete. */

import publicWidget from "@web/legacy/js/public/public_widget";

publicWidget.registry.WinnersComingSoonToast = publicWidget.Widget.extend({
    selector: ".o_winners_coming_soon_btn",
    events: {
        click: "_onClick",
    },

    _onClick(ev) {
        ev.preventDefault();
        this._showToast("Bientôt disponible");
    },

    _showToast(message) {
        const toast = document.createElement("div");
        toast.className = "o_winners_toast";
        toast.textContent = message;
        document.body.appendChild(toast);

        // Force le reflow pour que la transition d'entree s'applique.
        void toast.offsetWidth;
        toast.classList.add("o_winners_toast--visible");

        setTimeout(() => {
            toast.classList.remove("o_winners_toast--visible");
            setTimeout(() => toast.remove(), 300);
        }, 2500);
    },
});

export default publicWidget.registry.WinnersComingSoonToast;
