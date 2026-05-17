/**
 * monetique_theme — JavaScript principal
 * Menu mobile, scroll header, user dropdown, nav active
 */
(function () {
    'use strict';

    function initBurger() {
        var burger = document.getElementById('ssBurger');
        var nav = document.getElementById('ssNav');
        if (!burger || !nav) return;
        burger.addEventListener('click', function () {
            var open = nav.classList.toggle('open');
            burger.classList.toggle('open', open);
            burger.setAttribute('aria-expanded', String(open));
            document.body.style.overflow = open ? 'hidden' : '';
        });
        nav.querySelectorAll('.ss-nav-link').forEach(function (link) {
            link.addEventListener('click', function () {
                nav.classList.remove('open');
                burger.classList.remove('open');
                document.body.style.overflow = '';
            });
        });
        document.addEventListener('click', function (e) {
            if (!nav.contains(e.target) && !burger.contains(e.target)) {
                nav.classList.remove('open');
                burger.classList.remove('open');
                document.body.style.overflow = '';
            }
        });
    }

    function initNavActive() {
        var path = window.location.pathname;
        document.querySelectorAll('.ss-nav-link').forEach(function (link) {
            var href = (link.getAttribute('href') || '').split('?')[0];
            if (!href) return;
            if ((href === '/' && path === '/') || (href !== '/' && path.startsWith(href))) {
                link.classList.add('active');
            }
        });
    }

    function initRappelModal() {
        var btns = document.querySelectorAll('[data-rappel-trigger]');
        var modal = document.getElementById('ssRappelModal');
        if (!modal) return;
        btns.forEach(function (btn) {
            btn.addEventListener('click', function (e) {
                e.preventDefault();
                modal.style.display = 'flex';
                document.body.style.overflow = 'hidden';
            });
        });
        var close = modal.querySelector('[data-rappel-close]');
        if (close) {
            close.addEventListener('click', function () {
                modal.style.display = 'none';
                document.body.style.overflow = '';
            });
        }
        modal.addEventListener('click', function (e) {
            if (e.target === modal) {
                modal.style.display = 'none';
                document.body.style.overflow = '';
            }
        });
    }

    function initScrollReveal() {
        if (!('IntersectionObserver' in window)) return;
        var targets = document.querySelectorAll(
            '.ss-sol-card, .ss-hp-prod-card, .ss-garantie-card, .ss-stat-card, .ss-tarif-card'
        );
        if (!targets.length) return;
        var obs = new IntersectionObserver(function (entries) {
            entries.forEach(function (entry) {
                if (entry.isIntersecting) {
                    entry.target.style.opacity = '1';
                    entry.target.style.transform = 'translateY(0)';
                    obs.unobserve(entry.target);
                }
            });
        }, { threshold: 0.1, rootMargin: '0px 0px -30px 0px' });

        targets.forEach(function (el, i) {
            el.style.opacity = '0';
            el.style.transform = 'translateY(14px)';
            el.style.transition = 'opacity 0.45s ease ' + (i * 0.06) + 's, transform 0.45s ease ' + (i * 0.06) + 's';
            obs.observe(el);
        });
    }

    function init() {
        initBurger();
        initNavActive();
        initRappelModal();
        initScrollReveal();
    }

    if (document.readyState === 'loading') {
        document.addEventListener('DOMContentLoaded', init);
    } else {
        init();
    }
    document.addEventListener('page:loaded', init);
})();

/* ── Compteur statistiques (scroll reveal) ── */
function initCounters() {
    var counters = document.querySelectorAll('[data-counter]');
    if (!counters.length || !('IntersectionObserver' in window)) return;
    var obs = new IntersectionObserver(function(entries) {
        entries.forEach(function(entry) {
            if (!entry.isIntersecting) return;
            var el = entry.target;
            var target = parseInt(el.dataset.counter, 10);
            var suffix = el.dataset.suffix || '';
            var duration = 1500;
            var start = Date.now();
            var timer = setInterval(function() {
                var elapsed = Date.now() - start;
                var progress = Math.min(elapsed / duration, 1);
                var val = Math.round(progress * target);
                el.textContent = (val >= 1000 ? '+' + val.toLocaleString('fr-FR') : val) + suffix;
                if (progress >= 1) {
                    clearInterval(timer);
                    el.textContent = (target >= 1000 ? '+' + target.toLocaleString('fr-FR') : target) + suffix;
                }
            }, 16);
            obs.unobserve(el);
        });
    }, { threshold: 0.5 });
    counters.forEach(function(el) { obs.observe(el); });
}

/* ── Sélecteur type urgence ── */
function initUrgenceSelector() {
    document.querySelectorAll('.ss-urgence-check-item').forEach(function(item) {
        item.addEventListener('click', function() {
            var group = item.closest('.ss-urgence-check');
            group.querySelectorAll('.ss-urgence-check-item').forEach(function(i) {
                i.classList.remove('selected');
            });
            item.classList.add('selected');
            var input = document.querySelector('input[name="urgence"]');
            if (input) input.value = item.dataset.value || 'normale';
        });
    });
}

/* ── Extend init ── */
var _origInit = typeof init === 'function' ? init : function(){};
function init() {
    _origInit();
    initCounters();
    initUrgenceSelector();
}
