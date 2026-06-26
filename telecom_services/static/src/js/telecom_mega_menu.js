/** @odoo-module **/

const MEGA_MENU_EN = {
    title: 'Telecom Solutions for Professionals',
    subtitle: 'Voice, mobility, conversational intelligence, connectivity and cybersecurity.',
    cta: 'View catalogue',
};

function applyMegaMenuLang() {
    const lang = document.documentElement.lang || '';
    if (!lang.startsWith('en')) return;

    const container = document.querySelector('.o_mega_menu_telecom');
    if (!container) return;

    const title = container.querySelector('p.fw-bold');
    if (title) title.textContent = MEGA_MENU_EN.title;

    const subtitle = container.querySelector('p.mb-0');
    if (subtitle) subtitle.textContent = MEGA_MENU_EN.subtitle;

    const cta = container.querySelector('a.btn');
    if (cta) cta.textContent = MEGA_MENU_EN.cta;
}

function bindMegaMenuHover() {
    if (window.innerWidth < 992) return;
    document.querySelectorAll(
        '#top .nav-item:has(> .o_mega_menu_toggle)'
    ).forEach(li => {
        if (li._megaHoverBound) return;
        li._megaHoverBound = true;
        const toggle = li.querySelector('.o_mega_menu_toggle');
        const menu = li.querySelector('.o_mega_menu')
                  || li.querySelector('.dropdown-menu');
        if (!toggle) return;
        let leaveTimer;
        const cancelHide = () => clearTimeout(leaveTimer);
        const doShow = () => {
            li.classList.add('show');
            toggle.setAttribute('aria-expanded', 'true');
            if (menu) {
                menu.classList.add('show');
                ['transform', 'left', 'right', 'top', 'position', 'will-change']
                    .forEach(p => menu.style.removeProperty(p));
                const header = document.querySelector('#top');
                if (header) menu.style.top = header.getBoundingClientRect().bottom + 'px';
            }
        };
        const doHide = () => {
            li.classList.remove('show');
            toggle.setAttribute('aria-expanded', 'false');
            if (menu) menu.classList.remove('show');
        };
        const scheduleHide = () => {
            leaveTimer = setTimeout(() => {
                if (li.matches(':hover') ||
                    (menu && menu.matches(':hover'))) return;
                doHide();
            }, 200);
        };
        toggle.addEventListener('hide.bs.dropdown', e => {
            if (li.matches(':hover') ||
                (menu && menu.matches(':hover'))) e.preventDefault();
        });
        li.addEventListener('mouseenter', () => { cancelHide(); doShow(); });
        li.addEventListener('mouseleave', scheduleHide);
        if (menu) {
            menu.addEventListener('mouseenter', cancelHide);
            menu.addEventListener('mouseleave', scheduleHide);
        }
    });
}

if (document.readyState === 'loading') {
    document.addEventListener('DOMContentLoaded', () => {
        applyMegaMenuLang();
        bindMegaMenuHover();
    });
} else {
    applyMegaMenuLang();
    bindMegaMenuHover();
}
