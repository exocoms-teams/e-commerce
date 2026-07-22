document.addEventListener("DOMContentLoaded", function () {

    // HEADER STICKY 
    var header = document.querySelector(".sn-header");

    if (header) {
        var STICKY_THRESHOLD = 80; 

        window.addEventListener("scroll", function () {
            if (window.scrollY > STICKY_THRESHOLD) {
                header.classList.add("sn-header--sticky");
            } else {
                header.classList.remove("sn-header--sticky");
            }
        }, { passive: true });
    }

    // MENU HAMBURGER (mobile)
    var nav = document.querySelector(".sn-nav");

    if (nav && !document.querySelector(".sn-hamburger")) {
        var hamburger = document.createElement("button");
        hamburger.className  = "sn-hamburger";
        hamburger.setAttribute("aria-label", "Toggle navigation");
        hamburger.setAttribute("aria-expanded", "false");
        hamburger.innerHTML  =
            '<span></span><span></span><span></span>';

        var headerInner = document.querySelector(".sn-header .mn-container");
        if (headerInner) {
            headerInner.insertBefore(hamburger, nav);
        }

        hamburger.addEventListener("click", function () {
            var isOpen = nav.classList.toggle("sn-nav--open");
            hamburger.classList.toggle("sn-hamburger--active", isOpen);
            hamburger.setAttribute("aria-expanded", isOpen ? "true" : "false");

            document.body.style.overflow = isOpen ? "hidden" : "";
        });

        // Fermer en cliquant à l'extérieur
        document.addEventListener("click", function (e) {
            if (
                nav.classList.contains("sn-nav--open") &&
                !nav.contains(e.target) &&
                !hamburger.contains(e.target)
            ) {
                nav.classList.remove("sn-nav--open");
                hamburger.classList.remove("sn-hamburger--active");
                hamburger.setAttribute("aria-expanded", "false");
                document.body.style.overflow = "";
            }
        });

        // Fermer avec la touche Escape
        document.addEventListener("keydown", function (e) {
            if (e.key === "Escape" && nav.classList.contains("sn-nav--open")) {
                nav.classList.remove("sn-nav--open");
                hamburger.classList.remove("sn-hamburger--active");
                hamburger.setAttribute("aria-expanded", "false");
                document.body.style.overflow = "";
            }
        });
    }

    // SÉLECTEUR DE LANGUE
    var languageSwitcher = document.querySelector(".sn-language-switcher");

    if (languageSwitcher) {
        languageSwitcher.addEventListener("change", function () {
            var selectedLang = this.value;

            /* backend */
            console.log("[header.js] Langue sélectionnée :", selectedLang);
        });
    }

});
