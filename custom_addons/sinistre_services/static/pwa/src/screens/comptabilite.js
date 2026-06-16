/**
 * comptabilite.js — Module Comptabilité (style FairFair)
 */
window.Comptabilite = (function() {
    'use strict';

    let _data = null;
    let _facturesTab = 'du';
    let _paiementsTab = 'virements';

    function _fmtMoney(n) {
        return (Number(n) || 0).toLocaleString('fr-FR', { minimumFractionDigits: 2, maximumFractionDigits: 2 }) + ' €';
    }

    function _fmtDate(d) {
        if (!d) return '—';
        const dt = new Date(d);
        if (isNaN(dt)) return d;
        return dt.toLocaleDateString('fr-FR', { day: '2-digit', month: '2-digit', year: 'numeric' });
    }

    function _esc(s) {
        return String(s || '').replace(/&/g, '&amp;').replace(/</g, '&lt;').replace(/>/g, '&gt;');
    }

    function _badgeStatut(statut) {
        const ok = statut === 'Succès';
        return '<span class="acct-badge ' + (ok ? 'acct-badge-ok' : 'acct-badge-ko') + '">' + _esc(statut) + '</span>';
    }

    function init() {
        API.getComptabilite()
            .then(function(data) {
                _data = data;
                _renderHub();
                _renderFactures();
                _renderPaiements();
            })
            .catch(function() {
                _data = null;
                _renderHub();
            });
    }

    function showHub() {
        App.showSubView('comptabilite');
    }

    function showFactures() {
        App.showSubView('comptabilite-factures');
        _renderFactures();
    }

    function showPaiements() {
        App.showSubView('comptabilite-paiements');
        _renderPaiements();
    }

    function setFacturesTab(tab, btn) {
        _facturesTab = tab;
        document.querySelectorAll('#acctFacturesTabs .ff-tab').forEach(function(t) { t.classList.remove('active'); });
        if (btn) btn.classList.add('active');
        var head = document.getElementById('acctFacturesHead');
        if (head) {
            if (tab === 'travaux') {
                head.innerHTML = '<tr><th>ID</th><th>Dossier DU</th><th>BÉNÉFICIAIRE</th><th>VILLE</th><th>STATUT</th></tr>';
            } else {
                head.innerHTML = '<tr><th>ID</th><th>Ville</th><th>Statut</th><th>Date du RDV</th><th>Facture</th></tr>';
            }
        }
        _renderFacturesTable();
    }

    function setPaiementsTab(tab, btn) {
        _paiementsTab = tab;
        document.querySelectorAll('#acctPaiementsTabs .ff-tab').forEach(function(t) { t.classList.remove('active'); });
        if (btn) btn.classList.add('active');
        document.getElementById('acctVirementsPanel').style.display = tab === 'virements' ? 'block' : 'none';
        document.getElementById('acctDetailPanel').style.display = tab === 'detail' ? 'block' : 'none';
    }

    function _renderHub() {
        /* rien de dynamique sur le hub */
    }

    function _renderFactures() {
        _renderFacturesTable();
    }

    function _renderFacturesTable() {
        const tbody = document.getElementById('acctFacturesBody');
        if (!tbody) return;

        const rows = (_data && _data.factures && _data.factures[_facturesTab]) || [];
        if (!rows.length) {
            tbody.innerHTML = '<tr><td colspan="6" class="acct-empty">Aucune donnée</td></tr>';
            return;
        }

        if (_facturesTab === 'travaux') {
            tbody.innerHTML = rows.map(function(r) {
                return '<tr>'
                    + '<td>' + _esc(r.id) + '</td>'
                    + '<td>' + _esc(r.dossier_du) + '</td>'
                    + '<td>' + _esc(r.beneficiaire) + '</td>'
                    + '<td>' + _esc(r.ville) + '</td>'
                    + '<td>' + _badgeStatut(r.statut) + '</td>'
                    + '</tr>';
            }).join('');
            return;
        }

        tbody.innerHTML = rows.map(function(r) {
            return '<tr>'
                + '<td>' + _esc(r.id) + '</td>'
                + '<td>' + _esc(r.ville) + '</td>'
                + '<td>' + _badgeStatut(r.statut) + '</td>'
                + '<td>' + _fmtDate(r.date_rdv) + '</td>'
                + '<td>' + _esc(r.facture || '—') + '</td>'
                + '</tr>';
        }).join('');
    }

    function _renderPaiements() {
        const d = _data || {};
        const solde = d.solde || 0;
        const soldeEl = document.getElementById('acctSoldeValue');
        const soldeLbl = document.getElementById('acctSoldeLabel');
        const soldePill = document.querySelector('.acct-solde-pill');
        if (soldeEl) {
            soldeEl.textContent = Math.abs(solde).toLocaleString('fr-FR', { minimumFractionDigits: 2, maximumFractionDigits: 2 });
            soldeEl.className = 'acct-solde-value ' + (solde < 0 ? 'acct-solde-debit' : 'acct-solde-credit');
        }
        if (soldeLbl) soldeLbl.textContent = solde < 0 ? 'Solde débiteur (TTC)' : 'Solde créditeur (TTC)';
        if (soldePill) {
            soldePill.className = 'acct-solde-pill ' + (solde < 0 ? 'acct-solde-pill-debit' : 'acct-solde-pill-credit');
        }

        const caList = document.getElementById('acctCaList');
        if (caList) {
            const ca = d.ca_par_annee || [];
            caList.innerHTML = ca.length
                ? ca.map(function(item) {
                    return '<div class="acct-ca-row"><span>' + item.annee + '</span><span>' + _fmtMoney(item.montant) + '</span></div>';
                }).join('')
                : '<div class="acct-empty" style="padding:12px">Aucune donnée</div>';
        }

        const commBody = document.getElementById('acctCommissionsBody');
        if (commBody) {
            const comm = d.commissions || [];
            commBody.innerHTML = comm.map(function(c) {
                return '<tr>'
                    + '<td>' + _esc(c.type) + '</td>'
                    + '<td>' + _esc(c.intervention) + '</td>'
                    + '<td>' + _esc(c.pieces) + '</td>'
                    + '<td>' + _esc(c.total_ht) + '</td>'
                    + '</tr>';
            }).join('');
        }

        const virBody = document.getElementById('acctVirementsBody');
        if (virBody) {
            const vir = d.virements || [];
            virBody.innerHTML = vir.length
                ? vir.map(function(v) {
                    return '<tr>'
                        + '<td>' + _esc(v.date) + '</td>'
                        + '<td>' + _fmtMoney(v.montant_solde) + '</td>'
                        + '<td>' + _fmtMoney(v.commission) + '</td>'
                        + '<td>' + _fmtMoney(v.montant_paye) + '</td>'
                        + '<td>' + _fmtMoney(v.rac_facture) + '</td>'
                        + '<td>' + _fmtMoney(v.ca_genere) + '</td>'
                        + '</tr>';
                }).join('')
                : '<tr><td colspan="6" class="acct-empty">Aucune donnée</td></tr>';
        }

        _renderDetailSolde('du', 'acctDetailDuBody');
        _renderDetailSolde('travaux', 'acctDetailTravauxBody');
    }

    function _renderDetailSolde(key, elId) {
        const tbody = document.getElementById(elId);
        if (!tbody) return;
        const rows = (_data && _data.detail_solde && _data.detail_solde[key]) || [];
        tbody.innerHTML = rows.length
            ? rows.map(function(r) {
                return '<tr>'
                    + '<td>' + _esc(r.dossier) + '</td>'
                    + '<td>' + _esc(r.numero_facture) + '</td>'
                    + '<td>' + _fmtDate(r.date_facturation) + '</td>'
                    + '<td>' + _fmtMoney(r.montant_ht) + '</td>'
                    + '<td>' + _fmtMoney(r.montant_ttc) + '</td>'
                    + '</tr>';
            }).join('')
            : '<tr><td colspan="5" class="acct-empty">Aucune donnée</td></tr>';
    }

    function downloadCommissions() {
        const annee = document.getElementById('acctBatchAnnee')?.value;
        const trim = document.getElementById('acctBatchTrim')?.value;
        if (!annee || !trim) {
            Toast.show('Veuillez sélectionner une année et un trimestre', 'error');
            return;
        }
        Toast.show('Téléchargement des factures de commission — ' + trim + ' ' + annee, 'success');
    }

    return {
        init,
        showHub,
        showFactures,
        showPaiements,
        setFacturesTab,
        setPaiementsTab,
        downloadCommissions,
    };
})();
