/** @odoo-module **/

// Ouvre le méga-menu Télécom au survol (desktop ≥ 992 px) via l'API Bootstrap Dropdown,
// de sorte que survol et clic produisent le même résultat visuel.

function bindMegaMenuHover() {
    if (window.innerWidth < 992) return;

    document.querySelectorAll('#top .nav-item:has(> .o_mega_menu_toggle)').forEach(li => {
        if (li._megaHoverBound) return;
        li._megaHoverBound = true;

        const toggle = li.querySelector('.o_mega_menu_toggle');
        if (!toggle) return;

        // Le clic sur le lien ne doit pas basculer le dropdown (le survol suffit).
        toggle.addEventListener('click', e => {
            e.preventDefault();
            e.stopPropagation();
        });

        let leaveTimer;

        li.addEventListener('mouseenter', () => {
            clearTimeout(leaveTimer);
            window.bootstrap?.Dropdown.getOrCreateInstance(toggle).show();
        });

        li.addEventListener('mouseleave', () => {
            leaveTimer = setTimeout(() => {
                window.bootstrap?.Dropdown.getInstance(toggle)?.hide();
            }, 80);
        });
    });
}

document.addEventListener('DOMContentLoaded', bindMegaMenuHover);
