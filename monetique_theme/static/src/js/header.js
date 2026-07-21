document.addEventListener("DOMContentLoaded", () => {

    const languageSwitcher = document.querySelector(".sn-language-switcher");

    if (!languageSwitcher) {
        return;
    }

    languageSwitcher.addEventListener("change", function () {

        console.log("Selected language:", this.value);

        // À connecter plus tard au système de traduction d'Odoo.

    });

});