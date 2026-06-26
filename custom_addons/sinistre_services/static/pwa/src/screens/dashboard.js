/**
 * dashboard.js — Dashboard ArtisanPro
 * Remplace la mini-carte par une liste de missions proposées (à accepter/refuser)
 */

window.Dashboard = (() => {
    let _missions    = [];
    let _proposees   = [];
    let _interventions = [];
    let _metierFilter = 'all';
    let _statusFilter = 'all';
    let _intervFilter = 'all';
    let _searchQuery  = '';

    /* ── Badges ── */
    function _metierBadge(type) {
        const map = {
            serrurerie:     ['badge-serrurerie',  'Serrurerie'],
            plomberie:      ['badge-plomberie',   'Plomberie'],
            electricite:    ['badge-electricite', 'Électricité'],
            vitrerie:       ['badge-vitrerie',    'Vitrerie'],
            menuiserie_int: ['badge-autre',       'Menuiserie Int.'],
            menuiserie_ext: ['badge-autre',       'Menuiserie Ext.'],
            autre:          ['badge-autre',       'Autre'],
        };
        const [cls, label] = map[type] || ['badge-autre', type || '—'];
        return `<span class="badge ${cls}">${label}</span>`;
    }
    function _urgenceBadge(u) {
        if (u === 'tres_urgente') return `<span class="badge badge-urgente">🔴 Très urgente</span>`;
        if (u === 'urgente')      return `<span class="badge badge-urgente">🟠 Urgente</span>`;
        return '';
    }
    function _stateBadge(state) {
        const map = {
            nouveau:          ['badge-planifiee', 'Planifiée'],
            assigne:          ['badge-en-cours',  'En cours'],
            rdv_planifie:     ['badge-planifiee', 'Planifiée'],
            en_cours:         ['badge-en-cours',  'En cours'],
            travaux_en_cours: ['badge-en-cours',  'En cours'],
            termine:          ['badge-terminee',  'Terminée'],
            clos:             ['badge-terminee',  'Terminée'],
        };
        const [cls, label] = map[state] || ['badge-planifiee', 'Planifiée'];
        return `<span class="badge ${cls}">${label}</span>`;
    }

    /* ── Dates ── */
    function _fmtDate(d) {
        if (!d) return '—';
        return new Date(d).toLocaleDateString('fr-FR', { day:'numeric', month:'long', year:'numeric' });
    }
    function _fmtDateTime(d) {
        if (!d) return '—';
        const dt = new Date(d);
        const today = new Date();
        const tomorrow = new Date(); tomorrow.setDate(today.getDate() + 1);
        let day = dt.toDateString() === today.toDateString()    ? "Aujourd'hui"
                : dt.toDateString() === tomorrow.toDateString() ? 'Demain'
                : dt.toLocaleDateString('fr-FR', { day:'numeric', month:'short' });
        return `${day} · ${dt.toLocaleTimeString('fr-FR', { hour:'2-digit', minute:'2-digit' })}`;
    }

    /* ══════════════════════════════════════════════════════
       DASHBOARD
    ══════════════════════════════════════════════════════ */
    function _loadMissionsCache() {
        const cached = localStorage.getItem('ss_missions_cache');
        if (!cached) return;
        try { _missions = JSON.parse(cached); } catch (e) { _missions = []; }
    }

    async function _loadDashboard() {
        _loadMissionsCache();
        _updateDashStats();
        _renderToday();
        _renderProposeesList();

        try {
            const results = await Promise.all([
                API.getMissions().catch(function(err) {
                    console.warn('[Dashboard] getMissions:', err);
                    return { missions: _missions };
                }),
                API.getMissionsProposees().catch(function(err) {
                    console.warn('[Dashboard] getMissionsProposees:', err);
                    return { missions: [] };
                }),
            ]);
            _missions = (results[0] && results[0].missions) || _missions;
            _proposees = (results[1] && results[1].missions) || [];
            localStorage.setItem('ss_missions_cache', JSON.stringify(_missions));
        } catch (err) {
            console.warn('[Dashboard] load error:', err);
        } finally {
            _updateDashStats();
            _renderToday();
            _renderProposeesList();
            _loadExtendedStats();
        }
    }

    function _updateDashStats() {
        const ACTIVE = ['assigne','rdv_planifie','en_cours','devis_envoye','devis_accepte','travaux_en_cours','nouveau'];
        const actives = _missions.filter(m => ACTIVE.includes(m.state)).length;
        let user = {};
        try { user = JSON.parse(localStorage.getItem('ss_user') || '{}'); } catch(e) {}
        const nbInterv = user.interventions ?? 0;

        const el = id => document.getElementById(id);
        if (el('statActives'))      el('statActives').textContent      = actives;
        if (el('statInterventions'))el('statInterventions').textContent = nbInterv;
        if (el('statIntervTotal'))  el('statIntervTotal').textContent  = nbInterv;

        _updateExtendedStats(user);
    }

    function _fmtSolde(solde) {
        const val = Math.abs(Number(solde) || 0);
        return val.toLocaleString('fr-FR', { minimumFractionDigits: 2, maximumFractionDigits: 2 }) + ' €';
    }

    function _updateExtendedStats(user) {
        const solde = user.solde_comptabilite;
        const soldeEl = document.getElementById('statSolde');
        const soldeLbl = document.getElementById('statSoldeLabel');
        if (soldeEl && solde !== undefined && solde !== null) {
            soldeEl.textContent = _fmtSolde(solde);
            soldeEl.className = 'stat-value ' + (solde < 0 ? 'stat-solde-debit' : 'stat-solde-credit');
        }
        if (soldeLbl && solde !== undefined && solde !== null) {
            soldeLbl.textContent = solde < 0 ? 'Commission plateforme due (TTC)' : 'Solde créditeur (TTC)';
        }

        const taux = user.taux_acceptation;
        const tauxEl = document.getElementById('statTauxAccept');
        if (tauxEl) {
            if (taux === undefined || taux === null) {
                tauxEl.textContent = '—';
            } else {
                tauxEl.textContent = taux + ' %';
            }
        }

        const nbFactures = user.factures_a_fournir;
        const factEl = document.getElementById('statFacturesAFournir');
        if (factEl && nbFactures !== undefined && nbFactures !== null) {
            factEl.textContent = nbFactures;
        }
    }

    async function _loadExtendedStats() {
        try {
            const data = await API.getComptabilite();
            if (data && data.solde !== undefined) {
                let user = {};
                try { user = JSON.parse(localStorage.getItem('ss_user') || '{}'); } catch(e) {}
                user.solde_comptabilite = data.solde;
                localStorage.setItem('ss_user', JSON.stringify(user));
                _updateExtendedStats(user);
            }
        } catch (e) { /* fallback via /me */ }
    }

    function _renderToday() {
        const container = document.getElementById('todayList');
        if (!container) return;
        const ACTIVE = ['assigne','rdv_planifie','en_cours','devis_envoye','devis_accepte','travaux_en_cours','nouveau'];
        const items = _missions.filter(m => ACTIVE.includes(m.state));
        if (!items.length) {
            container.innerHTML = `
                <div class="empty-missions">
                    <div class="empty-missions-icon">📋</div>
                    <div class="empty-missions-title">Aucune mission en cours</div>
                    <div class="empty-missions-sub">Vos prochaines missions apparaîtront ici</div>
                </div>`;
            return;
        }
        container.innerHTML = items.slice(0, 5).map(m => {
            const addr  = m.adresse_intervention || m.adresse || '';
            const city  = addr.includes(',') ? addr.split(',').slice(-1)[0].trim() : addr;
            const title = m.description_sinistre || m.title || '—';
            const stateBadge = (m.urgence === 'urgente' || m.urgence === 'tres_urgente')
                ? _urgenceBadge(m.urgence) : _stateBadge(m.state);
            return `
                <div class="today-item" ${m.id ? `onclick="MissionDetail.open(${m.id})"` : ''} style="cursor:pointer">
                    <div class="today-item-top">${_metierBadge(m.type_intervention)}${stateBadge}</div>
                    <div class="today-item-title">${title}</div>
                    <div class="today-item-addr">${city}</div>
                    <div class="today-item-foot">
                        <span class="today-item-time">
                            <svg width="12" height="12" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2"><circle cx="12" cy="12" r="10"/><polyline points="12 6 12 12 16 14"/></svg>
                            ${_fmtDateTime(m.date_rdv)}
                        </span>
                    </div>
                </div>`;
        }).join('');
    }

    /* ══════════════════════════════════════════════════════
       MISSIONS PROPOSÉES (nouvelles — à accepter/refuser)
    ══════════════════════════════════════════════════════ */
    async function _loadProposees() {
        try {
            const data = await API.getMissionsProposees();
            _proposees = data.missions || [];
        } catch (err) {
            _proposees = [];
        }
        _renderProposeesList();
    }

    function _renderProposeesList() {
        const container = document.getElementById('proposeesList');
        const badge     = document.getElementById('proposeesBadge');
        if (!container) return;

        if (badge) badge.textContent = _proposees.length ? `${_proposees.length} disponible${_proposees.length > 1 ? 's' : ''}` : '';

        if (!_proposees.length) {
            container.innerHTML = `
                <div style="text-align:center;padding:40px 20px;color:#9CA3AF">
                    <div style="font-size:32px;margin-bottom:8px">🎯</div>
                    <div style="font-weight:600;font-size:14px;color:#374151;margin-bottom:4px">Aucune mission disponible</div>
                    <div style="font-size:13px">De nouvelles missions vous seront proposées prochainement</div>
                </div>`;
            return;
        }

        container.innerHTML = _proposees.map(m => _renderProposeeCard(m)).join('');
    }

    function _renderProposeeCard(m) {
        const addr     = m.adresse_intervention || m.adresse || '—';
        const desc     = m.description_sinistre || m.description || '—';
        const isUrgent = m.urgence === 'urgente' || m.urgence === 'tres_urgente';
        // Informations complémentaires sur la nature de l'intervention
        const details  = m.details_intervention || m.commentaire || '';

        return `
        <div class="proposee-card" id="proposee-${m.id}" style="
            border:1.5px solid ${isUrgent ? '#FCA5A5' : '#E5E7EB'};
            border-radius:14px;
            padding:16px;
            background:${isUrgent ? '#FFF7F7' : '#FAFAFA'};
            transition:box-shadow .15s;
        ">
            <div style="display:flex;align-items:flex-start;gap:8px;margin-bottom:10px;flex-wrap:wrap">
                ${_metierBadge(m.type_intervention)}
                ${_urgenceBadge(m.urgence)}
            </div>
            <div style="font-weight:600;font-size:14px;color:#111827;margin-bottom:6px;line-height:1.4">${desc}</div>
            ${details ? `<div style="font-size:13px;color:#6B7280;margin-bottom:6px;font-style:italic">${details}</div>` : ''}
            <div style="display:flex;align-items:center;gap:5px;font-size:13px;color:#6B7280;margin-bottom:4px">
                <svg width="13" height="13" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2"><circle cx="12" cy="10" r="3"/><path d="M12 21.7C17.3 17 20 13 20 10a8 8 0 1 0-16 0c0 3 2.7 6.9 8 11.7z"/></svg>
                ${addr}
            </div>
            ${m.date_rdv ? `
            <div style="display:flex;align-items:center;gap:5px;font-size:13px;color:#6B7280;margin-bottom:12px">
                <svg width="13" height="13" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2"><circle cx="12" cy="12" r="10"/><polyline points="12 6 12 12 16 14"/></svg>
                ${_fmtDateTime(m.date_rdv)}
            </div>` : '<div style="margin-bottom:12px"></div>'}
            <div style="display:flex;gap:8px">
                <button onclick="Dashboard.accepterMission(${m.id}, this)" style="
                    flex:1;background:#059669;color:#fff;border:none;border-radius:10px;
                    padding:10px;font-weight:700;font-size:13px;cursor:pointer;
                    display:flex;align-items:center;justify-content:center;gap:6px
                ">
                    <svg width="14" height="14" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2.5"><polyline points="20 6 9 17 4 12"/></svg>
                    Accepter
                </button>
                <button onclick="Dashboard.refuserMission(${m.id}, this)" style="
                    flex:1;background:#F3F4F6;color:#374151;border:none;border-radius:10px;
                    padding:10px;font-weight:600;font-size:13px;cursor:pointer;
                    display:flex;align-items:center;justify-content:center;gap:6px
                ">
                    <svg width="14" height="14" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2.5"><line x1="18" y1="6" x2="6" y2="18"/><line x1="6" y1="6" x2="18" y2="18"/></svg>
                    Refuser
                </button>
            </div>
        </div>`;
    }

    async function _refreshTauxAcceptation(tauxFromResponse) {
        let user = {};
        try { user = JSON.parse(localStorage.getItem('ss_user') || '{}'); } catch(e) {}

        /* null = aucune proposition aujourd'hui → afficher « — », ne pas rappeler /me */
        if (tauxFromResponse !== undefined) {
            user.taux_acceptation = tauxFromResponse;
            localStorage.setItem('ss_user', JSON.stringify(user));
            _updateExtendedStats(user);
            return;
        }

        try {
            const data = await API.getMe();
            if (data && data.user) {
                user.taux_acceptation = data.user.taux_acceptation ?? null;
                localStorage.setItem('ss_user', JSON.stringify(user));
                _updateExtendedStats(user);
            }
        } catch (e) { /* ignore */ }
    }

    async function accepterMission(missionId, btn) {
        if (btn) {
            btn.disabled = true;
            btn.textContent = '…';
        }
        try {
            const result = await API.accepterMissionProposee(missionId);

            const card = document.getElementById(`proposee-${missionId}`);
            if (card) {
                card.style.transition = 'opacity .3s, transform .3s';
                card.style.opacity = '0';
                card.style.transform = 'translateX(20px)';
                setTimeout(() => card.remove(), 300);
            }
            _proposees = _proposees.filter(m => m.id !== missionId);
            const badge = document.getElementById('proposeesBadge');
            if (badge) badge.textContent = _proposees.length ? `${_proposees.length} disponible${_proposees.length > 1 ? 's' : ''}` : '';

            Toast.show('✅ Mission acceptée — elle est dans Mes Missions', 'success');

            try {
                const data = await API.getMissions();
                _missions = data.missions || [];
                localStorage.setItem('ss_missions_cache', JSON.stringify(_missions));
                _updateDashStats();
                _renderToday();
            } catch (e) { /* cache local inchangé */ }

            await _refreshTauxAcceptation(
                result && Object.prototype.hasOwnProperty.call(result, 'taux_acceptation')
                    ? result.taux_acceptation
                    : undefined
            );
        } catch(err) {
            Toast.show('Erreur: ' + err.message, 'error');
            if (btn) {
                btn.disabled = false;
                btn.textContent = 'Accepter';
            }
        }
    }

    async function refuserMission(missionId, btn, skipConfirm) {
        if (!skipConfirm && !confirm('Refuser cette mission ?')) return;
        if (btn) btn.disabled = true;
        try {
            const result = await API.refuserMissionProposee(missionId);
            const card = document.getElementById(`proposee-${missionId}`);
            if (card) {
                card.style.transition = 'opacity .3s';
                card.style.opacity = '0';
                setTimeout(() => card.remove(), 300);
            }
            Toast.show('Mission refusée', 'warning');
            _proposees = _proposees.filter(m => m.id !== missionId);
            const badge = document.getElementById('proposeesBadge');
            if (badge) badge.textContent = _proposees.length ? `${_proposees.length} disponible${_proposees.length > 1 ? 's' : ''}` : '';
            if (!_proposees.length) {
                const container = document.getElementById('proposeesList');
                if (container) container.innerHTML = `
                    <div style="text-align:center;padding:40px 20px;color:#9CA3AF">
                        <div style="font-size:32px;margin-bottom:8px">🎯</div>
                        <div style="font-weight:600;font-size:14px;color:#374151;margin-bottom:4px">Aucune mission disponible</div>
                        <div style="font-size:13px">De nouvelles missions vous seront proposées prochainement</div>
                    </div>`;
            }
            await _refreshTauxAcceptation(
                result && Object.prototype.hasOwnProperty.call(result, 'taux_acceptation')
                    ? result.taux_acceptation
                    : undefined
            );
        } catch(err) {
            Toast.show('Erreur: ' + err.message, 'error');
            if (btn) btn.disabled = false;
        }
    }

    /* ══════════════════════════════════════════════════════
       MISSIONS EN COURS
    ══════════════════════════════════════════════════════ */
    function loadMissions() {
        const container = document.getElementById('missionsList');
        if (!container) return;
        container.innerHTML = '<div class="skeleton-card-h"></div><div class="skeleton-card-h"></div>';
        const ACTIVE = ['assigne','rdv_planifie','en_cours','devis_envoye','devis_accepte','travaux_en_cours','nouveau'];
        API.getMissions().then(data => {
            _missions = data.missions || [];
            localStorage.setItem('ss_missions_cache', JSON.stringify(_missions));
        }).catch(() => {}).finally(() => {
            const missions = _missions.filter(m => ACTIVE.includes(m.state));
            const sub = document.getElementById('missionsSubtitle');
            if (sub) sub.textContent = missions.length + ' mission(s) active(s)';
            _renderMissions(missions);
        });
    }

    function _renderMissions(missions) {
        let filtered = missions.filter(m => {
            if (_metierFilter !== 'all' && m.type_intervention !== _metierFilter) return false;
            if (_statusFilter === 'urgente' && m.urgence !== 'urgente' && m.urgence !== 'tres_urgente') return false;
            if (_statusFilter === 'en_cours' && !['en_cours','travaux_en_cours','assigne'].includes(m.state)) return false;
            if (_statusFilter === 'planifiee' && !['rdv_planifie','nouveau'].includes(m.state)) return false;
            if (_searchQuery) {
                const q = _searchQuery.toLowerCase();
                const hay = ((m.description_sinistre||'')+(m.client||'')+(m.adresse_intervention||'')).toLowerCase();
                if (!hay.includes(q)) return false;
            }
            return true;
        });

        const container = document.getElementById('missionsList');
        if (!container) return;

        if (!filtered.length) {
            const isFiltered = _metierFilter !== 'all' || _statusFilter !== 'all' || _searchQuery;
            container.innerHTML = `
                <div class="empty-state-full">
                    <div class="empty-state-icon">${isFiltered ? '🔍' : '📋'}</div>
                    <div class="empty-state-title">${isFiltered ? 'Aucun résultat' : 'Aucune mission en cours'}</div>
                    <div class="empty-state-sub">${isFiltered ? 'Modifiez vos filtres' : "Vous n'avez pas encore de missions assignées"}</div>
                </div>`;
            return;
        }

        container.innerHTML = filtered.map(m => `
            <div class="mission-card-h">
                <div class="mc-top">
                    ${_metierBadge(m.type_intervention)}
                    ${_urgenceBadge(m.urgence)}
                    <span class="mc-ref">Réf. ${m.reference}</span>
                    <div style="text-align:right"><div style="font-size:11px;color:#9CA3AF">Client : ${m.client||'—'}</div></div>
                </div>
                <div class="mc-title">${m.description_sinistre||m.description||'—'}</div>
                <div class="mc-meta">
                    <span class="mc-meta-item">
                        <svg width="13" height="13" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2"><circle cx="12" cy="10" r="3"/><path d="M12 21.7C17.3 17 20 13 20 10a8 8 0 1 0-16 0c0 3 2.7 6.9 8 11.7z"/></svg>
                        ${m.adresse_intervention||m.adresse||'—'}
                    </span>
                    <span class="mc-meta-item">
                        <svg width="13" height="13" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2"><circle cx="12" cy="12" r="10"/><polyline points="12 6 12 12 16 14"/></svg>
                        ${_fmtDateTime(m.date_rdv)}
                    </span>
                </div>
                <div class="mc-actions">
                    <button class="btn-start" onclick="MissionDetail&&MissionDetail.open(${JSON.stringify(m.id||m.reference)})">Ouvrir la mission</button>
                    <button class="btn-call" onclick="window.location.href='tel:${m.tel_sur_place||''}'">
                        <svg width="13" height="13" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2"><path d="M22 16.92v3a2 2 0 0 1-2.18 2 19.79 19.79 0 0 1-8.63-3.07A19.5 19.5 0 0 1 4.69 13.5 19.79 19.79 0 0 1 1.6 4.86C1.6 3.82 2.4 3 3.44 3h3a2 2 0 0 1 2 1.72c.127.96.361 1.903.7 2.81a2 2 0 0 1-.45 2.11L7.91 10.4a16 16 0 0 0 6 6l.78-.78a2 2 0 0 1 2.11-.45c.907.339 1.85.573 2.81.7A2 2 0 0 1 21.28 18z"/></svg>
                        Appeler client
                    </button>
                </div>
            </div>
        `).join('');
    }

    /* ══════════════════════════════════════════════════════
       INTERVENTIONS RÉALISÉES
    ══════════════════════════════════════════════════════ */
    let _facturesAFournir = [];

    function loadInterventions() {
        API.getMissionsHistorique().then(function(data) {
            _missions = data.missions || [];
            localStorage.setItem('ss_missions_cache', JSON.stringify(_missions));
        }).catch(function() {
            const cached = localStorage.getItem('ss_missions_cache');
            if (cached) { try { _missions = JSON.parse(cached); } catch(e) {} }
        }).finally(function() {
            const apiTerminees = _missions
                .filter(m => ['termine', 'facture', 'clos'].includes(m.state))
                .map(m => ({
                    id: m.id,
                    ref: m.reference, date: m.date_cloture || m.date_rdv, client: m.client,
                    type: m.type_intervention, prestation: m.description_sinistre,
                    addr: m.adresse_intervention,
                }));
            _interventions = apiTerminees;
            _renderInterventions();
            const total = _interventions.length;
            const el = id => document.getElementById(id);
            if (el('statIntervTotal')) el('statIntervTotal').textContent = total;
            _loadFacturesAFournir();
        });
    }

    function _loadFacturesAFournir() {
        const tbody = document.getElementById('facturesAFournirBody');
        if (tbody) {
            tbody.innerHTML = '<tr><td colspan="7" style="text-align:center;padding:40px;color:#9CA3AF">Chargement…</td></tr>';
        }
        API.getFacturesAFournir()
            .then(function(data) {
                _facturesAFournir = data.factures || [];
                let user = {};
                try { user = JSON.parse(localStorage.getItem('ss_user') || '{}'); } catch(e) {}
                user.factures_a_fournir = data.count || _facturesAFournir.length;
                localStorage.setItem('ss_user', JSON.stringify(user));
                _updateExtendedStats(user);
                _renderFacturesAFournir();
            })
            .catch(function() {
                _facturesAFournir = [];
                _renderFacturesAFournir();
            });
    }

    function _facturerMission(missionId, reference) {
        if (!missionId) {
            Toast.show('Mission introuvable', 'error');
            return;
        }
        const label = reference || missionId;
        if (!confirm('Générer la facture pour la mission ' + label + ' ?')) return;
        API.facturerMission(missionId)
            .then(function(data) {
                const num = (data && data.facture_numero) ? data.facture_numero : '';
                Toast.show(num ? ('Facture ' + num + ' créée') : 'Facture créée avec succès', 'success');
                _loadFacturesAFournir();
                loadInterventions();
                if (window.Comptabilite && Comptabilite.init) Comptabilite.init();
                if (window.Dashboard && Dashboard.updateExtendedStats) {
                    API.getComptabilite().then(function(acct) {
                        if (acct && acct.solde !== undefined) {
                            let user = {};
                            try { user = JSON.parse(localStorage.getItem('ss_user') || '{}'); } catch(e) {}
                            user.solde_comptabilite = acct.solde;
                            user.factures_a_fournir = Math.max(0, (user.factures_a_fournir || 1) - 1);
                            localStorage.setItem('ss_user', JSON.stringify(user));
                            Dashboard.updateExtendedStats(user);
                        }
                    }).catch(function() {});
                }
            })
            .catch(function(err) {
                Toast.show(err.message || 'Erreur lors de la facturation', 'error');
            });
    }

    function _renderFacturesAFournir() {
        const tbody = document.getElementById('facturesAFournirBody');
        const badge = document.getElementById('facturesAFournirBadge');
        const count = _facturesAFournir.length;
        if (badge) {
            badge.textContent = count ? count + ' en attente' : '';
            badge.style.display = count ? 'inline-block' : 'none';
        }
        if (!tbody) return;
        if (!count) {
            tbody.innerHTML = '<tr><td colspan="7"><div class="empty-state-full" style="padding:40px 0"><div class="empty-state-icon">✅</div><div class="empty-state-title">Toutes vos factures sont à jour</div></div></td></tr>';
            return;
        }
        tbody.innerHTML = _facturesAFournir.map(function(f) {
            const montant = (Number(f.montant_devis) || 0).toLocaleString('fr-FR', { minimumFractionDigits: 2, maximumFractionDigits: 2 }) + ' €';
            return '<tr>'
                + '<td class="interv-ref">' + (f.reference || '—') + '</td>'
                + '<td class="interv-date">' + _fmtDate(f.date) + '</td>'
                + '<td>' + (f.client || '—') + '</td>'
                + '<td>' + _metierBadge(f.type_intervention) + '</td>'
                + '<td><div style="font-weight:600;font-size:13.5px">' + (f.prestation || '—') + '</div><div style="font-size:12px;color:#9CA3AF">' + (f.adresse || '') + '</div></td>'
                + '<td style="font-weight:700">' + montant + '</td>'
                + '<td><button class="btn-start" style="padding:8px 14px;font-size:12px" onclick="Dashboard.facturerMission(' + f.id + ', \'' + (f.reference || '').replace(/'/g, "\\'") + '\')">Facturer</button></td>'
                + '</tr>';
        }).join('');
    }

    function scrollToFactures() {
        const section = document.getElementById('intervFacturesSection');
        if (section) section.scrollIntoView({ behavior: 'smooth', block: 'start' });
    }

    function _renderInterventions() {
        const tbody = document.getElementById('intervTableBody');
        if (!tbody) return;
        const list = _intervFilter === 'all' ? _interventions : _interventions.filter(i => i.type === _intervFilter);
        if (!list.length) {
            tbody.innerHTML = `<tr><td colspan="7"><div class="empty-state-full" style="padding:60px 0"><div class="empty-state-icon">✅</div><div class="empty-state-title">Aucune intervention terminée</div></div></td></tr>`;
            return;
        }
        tbody.innerHTML = list.map(i => `
            <tr class="interv-row-clickable" onclick="MissionDetail.open(${i.id})" title="Voir le récapitulatif">
                <td class="interv-ref">${i.ref}</td>
                <td class="interv-date">${_fmtDate(i.date)}</td>
                <td>${i.client||'—'}</td>
                <td>${_metierBadge(i.type)}</td>
                <td><div style="font-weight:600;font-size:13.5px">${i.prestation||'—'}</div><div style="font-size:12px;color:#9CA3AF">${i.addr||''}</div></td>
                <td><span class="badge badge-terminee">Terminée</span></td>
            </tr>`).join('');
    }

    /* ── Carte (compatibilité) ── */
    function initCarte() {}
    function _renderCarteNext() {}

    /* ── Filtres ── */
    function setMetierFilter(val, btn) {
        _metierFilter = val;
        document.querySelectorAll('#metierFilters .tag-btn').forEach(b => b.classList.remove('active'));
        btn.classList.add('active');
        _renderMissions(_missions.filter(m => ['assigne','rdv_planifie','en_cours','devis_envoye','devis_accepte','travaux_en_cours','nouveau'].includes(m.state)));
    }
    function setStatusFilter(val, btn) {
        _statusFilter = val;
        document.querySelectorAll('#statusFilters .tag-btn').forEach(b => b.classList.remove('active'));
        btn.classList.add('active');
        _renderMissions(_missions.filter(m => ['assigne','rdv_planifie','en_cours','devis_envoye','devis_accepte','travaux_en_cours','nouveau'].includes(m.state)));
    }
    function setIntervFilter(val, btn) {
        _intervFilter = val;
        document.querySelectorAll('.interv-filters .tag-btn').forEach(b => b.classList.remove('active'));
        btn.classList.add('active');
        _renderInterventions();
    }
    function filterMissions() {
        _searchQuery = (document.getElementById('missionsSearch')||{}).value || '';
        _renderMissions(_missions.filter(m => ['assigne','rdv_planifie','en_cours','devis_envoye','devis_accepte','travaux_en_cours','nouveau'].includes(m.state)));
    }

    return {
        init() { _loadDashboard(); },
        loadMissions,
        loadInterventions,
        initCarte,
        accepterMission,
        refuserMission,
        scrollToFactures,
        facturerMission: _facturerMission,
        updateExtendedStats: _updateExtendedStats,
        // Legacy
        acceptMission() {},
        itineraireMission() {},
        setMetierFilter,
        setStatusFilter,
        setIntervFilter,
        filterMissions,
        showMapPin() {},
        refresh() { _loadDashboard(); },
        setFilter() {},
    };
})();
