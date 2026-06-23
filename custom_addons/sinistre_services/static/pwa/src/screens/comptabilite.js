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

    function _renderHub() {
        const card = document.getElementById('acctFacturesAFournirCard');
        const list = document.getElementById('acctFacturesAFournirList');
        const pending = (_data && _data.factures_a_fournir) || [];
        if (!card || !list) return;
        if (!pending.length) {
            card.style.display = 'none';
            return;
        }
        card.style.display = 'block';
        list.innerHTML = pending.slice(0, 5).map(function(f) {
            const montant = _fmtMoney(f.montant_devis);
            return '<div style="display:flex;align-items:center;justify-content:space-between;gap:12px;padding:10px 0;border-bottom:1px solid #F3F4F6">'
                + '<div><div style="font-weight:600;font-size:13px">' + _esc(f.reference) + ' — ' + _esc(f.prestation || 'Mission') + '</div>'
                + '<div style="font-size:12px;color:#6B7280">' + _esc(f.client) + ' · ' + montant + '</div></div>'
                + '<button class="btn-start" style="padding:6px 12px;font-size:12px;white-space:nowrap" onclick="Comptabilite.facturerMission(' + f.id + ')">Facturer</button>'
                + '</div>';
        }).join('');
        if (pending.length > 5) {
            list.innerHTML += '<p style="font-size:12px;color:#9CA3AF;margin-top:8px">+' + (pending.length - 5) + ' autre(s) — voir Interventions</p>';
        }
    }

    function _downloadExport(path) {
        const url = CONFIG.ODOO_BASE_URL + CONFIG.API_BASE + path;
        window.open(url, '_blank');
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
                head.innerHTML = '<tr><th>ID</th><th>Dossier DU</th><th>BÉNÉFICIAIRE</th><th>VILLE</th><th>STATUT</th><th>Action</th></tr>';
            } else {
                head.innerHTML = '<tr><th>ID</th><th>Ville</th><th>Statut</th><th>Date du RDV</th><th>Facture</th><th>Action</th></tr>';
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
                var action = r.a_facturer
                    ? '<button class="btn-start" style="padding:6px 12px;font-size:12px" onclick="Comptabilite.facturerMission(' + r.id + ')">Facturer</button>'
                    : (r.facture ? '—' : '—');
                return '<tr>'
                    + '<td>' + _esc(r.id) + '</td>'
                    + '<td>' + _esc(r.dossier_du) + '</td>'
                    + '<td>' + _esc(r.beneficiaire) + '</td>'
                    + '<td>' + _esc(r.ville) + '</td>'
                    + '<td>' + _badgeStatut(r.statut) + '</td>'
                    + '<td>' + action + '</td>'
                    + '</tr>';
            }).join('');
            return;
        }

        tbody.innerHTML = rows.map(function(r) {
            var factureCell = r.facture
                ? _esc(r.facture)
                : '<span style="color:#9CA3AF">À facturer</span>';
            var action = r.a_facturer
                ? '<button class="btn-start" style="padding:6px 12px;font-size:12px" onclick="Comptabilite.facturerMission(' + r.id + ')">Facturer</button>'
                : '—';
            return '<tr>'
                + '<td>' + _esc(r.id) + '</td>'
                + '<td>' + _esc(r.ville) + '</td>'
                + '<td>' + _badgeStatut(r.statut) + '</td>'
                + '<td>' + _fmtDate(r.date_rdv || r.date_cloture) + '</td>'
                + '<td>' + factureCell + '</td>'
                + '<td>' + action + '</td>'
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
        if (soldeLbl) soldeLbl.textContent = solde < 0 ? 'Commission plateforme due (TTC)' : 'Solde créditeur (TTC)';
        if (soldePill) {
            soldePill.className = 'acct-solde-pill ' + (solde < 0 ? 'acct-solde-pill-debit' : 'acct-solde-pill-credit');
        }
        var soldeHint = document.getElementById('acctSoldeHint');
        if (soldeHint) {
            soldeHint.textContent = solde < 0
                ? 'Montant de commission à régler à la plateforme sur vos interventions facturées.'
                : 'Crédit disponible sur votre compte artisan.';
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
            : '<tr><td colspan="5" class="acct-empty">Aucune facture émise — utilisez « Facturer » dans Gérer mes factures ou Interventions.</td></tr>';
    }

    function facturerMission(missionId) {
        if (!missionId) {
            Toast.show('Mission introuvable', 'error');
            return;
        }
        if (!confirm('Générer la facture pour cette mission ?')) return;
        API.facturerMission(missionId)
            .then(function(data) {
                var num = (data && data.facture_numero) ? data.facture_numero : '';
                Toast.show(num ? ('Facture ' + num + ' créée') : 'Facture créée avec succès', 'success');
                return init();
            })
            .catch(function(err) {
                Toast.show(err.message || 'Erreur lors de la facturation', 'error');
            });
    }

    function downloadCommissions() {
        const annee = document.getElementById('acctBatchAnnee')?.value;
        const trim = document.getElementById('acctBatchTrim')?.value;
        if (!annee || !trim) {
            Toast.show('Veuillez sélectionner une année et un trimestre', 'error');
            return;
        }
        _downloadExport('/intervenant/comptabilite/commissions?annee=' + encodeURIComponent(annee) + '&trimestre=' + encodeURIComponent(trim));
        Toast.show('Téléchargement commissions ' + trim + ' ' + annee, 'success');
    }

    function exportFactures() {
        _downloadExport('/intervenant/comptabilite/export?type=factures&tab=' + encodeURIComponent(_facturesTab));
    }

    function exportVirements() {
        _downloadExport('/intervenant/comptabilite/export?type=virements');
    }

    function exportDetail() {
        _downloadExport('/intervenant/comptabilite/export?type=detail');
    }

    function exportFacturesAFournir() {
        _downloadExport('/intervenant/comptabilite/export?type=factures_a_fournir');
    }

    return {
        init,
        showHub,
        showFactures,
        showPaiements,
        setFacturesTab,
        setPaiementsTab,
        facturerMission,
        downloadCommissions,
        exportFactures,
        exportVirements,
        exportDetail,
        exportFacturesAFournir,
    };
})();
