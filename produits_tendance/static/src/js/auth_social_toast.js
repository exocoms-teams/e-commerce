/* WIN-121 : Boutons de connexion sociale non fonctionnels.
 * Affiche un toast "Bientôt disponible" au clic, sans déclencher
 * aucune requête ni logique d'authentification. */
(function () {
    "use strict";

    function showToast(message) {
        var existing = document.querySelector(".o_winners_toast");
        if (existing) {
            existing.remove();
        }

        var toast = document.createElement("div");
        toast.className = "o_winners_toast";
        toast.textContent = message;
        document.body.appendChild(toast);

        // Force reflow to enable the transition on next frame.
        requestAnimationFrame(function () {
            toast.classList.add("o_winners_toast_visible");
        });

        setTimeout(function () {
            toast.classList.remove("o_winners_toast_visible");
            setTimeout(function () {
                toast.remove();
            }, 250);
        }, 2500);
    }

    document.addEventListener("click", function (ev) {
        var btn = ev.target.closest(".o_winners_social_btn");
        if (!btn) {
            return;
        }
        ev.preventDefault();
        showToast("Bientôt disponible");
    });
})();
