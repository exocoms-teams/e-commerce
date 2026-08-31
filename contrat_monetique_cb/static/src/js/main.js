/**
 * Contrat monétique CB — animation au scroll
 */
(function () {
    'use strict';

    document.documentElement.classList.add('cmq-js', 'cmcb-js');

    var delayPool = ['1', '2', '3', '4', '5', '6', '7', '8'];

    // Blocs racine animés, puis leurs enfants en cascade.
    var sections = document.querySelectorAll(
        '.cmq-section, .cmq-calc, .cmq-final-wrap, ' +
        '.cmcb-section, .cmcb-calc, .cmcb-cta, .cmcb-proof'
    );

    var revealTargets = function (root, baseIndex) {
        var children = [];
        var container = root.querySelector(':scope > .cmcb-container');
        if (container && container.children.length) {
            children = Array.prototype.slice.call(container.children);
        } else {
            children = [root];
        }
        children.forEach(function (el, i) {
            el.classList.add('reveal');
            el.setAttribute('data-delay', delayPool[(baseIndex + i) % delayPool.length]);
        });
        return children;
    };

    var hero = document.querySelector('.cmcb-hero');
    var prepared = [];
    if (hero) {
        var heroChildren = [];
        var heroContainer = hero.querySelector(':scope > .cmcb-container');
        if (heroContainer && heroContainer.children.length) {
            heroChildren = Array.prototype.slice.call(heroContainer.children);
        } else {
            heroChildren = [hero];
        }
        heroChildren.forEach(function (el, i) {
            el.classList.add('reveal');
            el.setAttribute('data-delay', delayPool[i % delayPool.length]);
            prepared.push(el);
        });
    }

    sections.forEach(function (section) {
        prepared = prepared.concat(revealTargets(section, 0));
    });

    if (!prepared.length) {
        return;
    }

    // Animation au scroll : les blocs sont cachés puis révélés quand ils
    // entrent dans le viewport. Sans JS, tout reste visible.
    var observer = new IntersectionObserver(function (entries) {
        entries.forEach(function (entry) {
            if (entry.isIntersecting) {
                entry.target.classList.add('is-in');
                observer.unobserve(entry.target);
            }
        });
    }, { threshold: 0.12, rootMargin: '0px 0px -8% 0px' });

    prepared.forEach(function (el) {
        var rect = el.getBoundingClientRect();
        if (rect.top < window.innerHeight && rect.bottom > 0) {
            el.classList.add('is-in');
        } else {
            observer.observe(el);
        }
    });
})();

/**
 * Contrat monétique CB — simulateur d'économies
 */
(function () {
    'use strict';

    var ca = document.getElementById('cmq-ca');
    var taux = document.getElementById('cmq-taux');
    var tpe = document.getElementById('cmq-tpe');
    if (!ca) return;

    var fmtEUR = function (n) {
        return n.toLocaleString('fr-FR', { minimumFractionDigits: 2, maximumFractionDigits: 2 }) + '\u00a0€';
    };
    var fmtEUR0 = function (n) {
        return Math.round(n).toLocaleString('fr-FR') + '\u00a0€';
    };

    var BLUE = getComputedStyle(document.documentElement).getPropertyValue('--mq-blue').trim() || '#0D47A1';

    function updateSliderBackground(slider) {
        var min = parseFloat(slider.min);
        var max = parseFloat(slider.max);
        var val = parseFloat(slider.value);
        var pct = ((val - min) / (max - min)) * 100;
        slider.style.background = 'linear-gradient(to right, ' + BLUE + ' 0%, ' + BLUE + ' ' + pct + '%, #E2E8F0 ' + pct + '%, #E2E8F0 100%)';
    }

    function update() {
        var vCA = parseFloat(ca.value);
        var vTaux = parseFloat(taux.value);
        var vTPE = parseFloat(tpe.value);

        document.getElementById('cmq-ca-val').textContent = fmtEUR0(vCA);
        document.getElementById('cmq-taux-val').textContent = vTaux.toLocaleString('fr-FR', { minimumFractionDigits: 2, maximumFractionDigits: 2 }) + '\u00a0%';
        document.getElementById('cmq-tpe-val').textContent = fmtEUR0(vTPE);

        var comBq = vCA * vTaux / 100;
        var totBq = comBq + vTPE;
        var comExo = vCA * 0.25 / 100;
        var save = Math.max(0, totBq - comExo);

        document.getElementById('cmq-r-taux').textContent = vTaux.toLocaleString('fr-FR', { minimumFractionDigits: 2, maximumFractionDigits: 2 });
        document.getElementById('cmq-r-combq').textContent = fmtEUR(comBq);
        document.getElementById('cmq-r-loc').textContent = fmtEUR(vTPE);
        document.getElementById('cmq-r-totbq').textContent = fmtEUR(totBq);
        document.getElementById('cmq-r-comexo').textContent = fmtEUR(comExo);
        document.getElementById('cmq-r-totexo').textContent = fmtEUR(comExo);
        document.getElementById('cmq-r-save').textContent = fmtEUR(save) + ' / mois';
        document.getElementById('cmq-r-savey').textContent = 'soit ' + fmtEUR0(save * 12) + ' / an';

        updateSliderBackground(ca);
        updateSliderBackground(taux);
        updateSliderBackground(tpe);
    }

    [ca, taux, tpe].forEach(function (el) {
        el.addEventListener('input', update);
    });
    update();
})();
