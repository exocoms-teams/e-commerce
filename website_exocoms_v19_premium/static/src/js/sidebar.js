
/** @odoo-module **/

document.addEventListener("DOMContentLoaded", function () {
    if (!document.body.classList.contains("exo-theme")) return;
    if (document.querySelector(".exo-custom-sidebar")) return;

    const sidebar = document.createElement("aside");
    sidebar.className = "exo-custom-sidebar";
    sidebar.setAttribute("aria-label", "Navigation EXOCOMS");

    sidebar.innerHTML = `
        <div class="exo-brand">
            <div class="exo-brand-x">X</div>
            <div class="exo-brand-name">EXOCOMS</div>
            <div class="exo-brand-tagline">
                Connecter. Sécuriser. Développer.
            </div>
        </div>

        <nav class="exo-side-nav" aria-label="Menu principal">

            <a href="/" class="exo-active" aria-current="page">
                <span aria-hidden="true">⌂</span> Accueil
            </a>

            <details open>
                <summary>
                    <span aria-hidden="true">▦</span> Nos Solutions
                </summary>

                <div class="exo-submenu">
                    <a href="/monetique">Monétique</a>
                    <a href="/informatique">Informatique</a>
                    <a href="/videosurveillance">Vidéosurveillance</a>
                    <a href="/securite">Sécurité</a>
                    <a href="/wifi">WiFi</a>
                </div>
            </details>

            <a href="/secteurs">
                <span aria-hidden="true">▦</span> Secteurs d'activité
            </a>

            <a href="/aboutus">
                <span aria-hidden="true">♙</span> À propos
            </a>

            <a href="/support">
                <span aria-hidden="true">◉</span> Support
            </a>

            <a href="/contactus">
                <span aria-hidden="true">✉</span> Contact
            </a>

        </nav>

        <div class="exo-sidebar-bottom">
            <div class="exo-help">
                <div class="exo-help-icon" aria-hidden="true">☎</div>
                <strong>Besoin d'aide ?</strong>
                <a href="tel:0184600000">01 84 60 00 00</a>
                <small>Support 24/7</small>
            </div>
        </div>
    `;

    document.body.prepend(sidebar);
    document.body.classList.add("exo-has-sidebar");
});
