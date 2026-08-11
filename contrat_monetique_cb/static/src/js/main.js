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
    }

    [ca, taux, tpe].forEach(function (el) {
        el.addEventListener('input', update);
    });
    update();
})();
