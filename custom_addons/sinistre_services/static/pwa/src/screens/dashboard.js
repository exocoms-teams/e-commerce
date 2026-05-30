/**
 * dashboard.js — Dashboard Desktop ArtisanPro
 * Gère : tableau de bord, missions, interventions, carte
 */

window.Dashboard = (() => {
    let _missions = [];
    let _interventions = [];
    let _metierFilter = 'all';
    let _statusFilter = 'all';
    let _intervFilter = 'all';
    let _searchQuery = '';
    let _currentMapPin = null;

    // Pins de carte — alimentés par les missions réelles
    const MAP_PINS = [];

    /* ── Badge helpers ── */
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
        if (u === 'tres_urgente' || u === 'urgente') return `<span class="badge badge-urgente">Urgente</span>`;
        return '';
    }

    function _stateBadge(state) {
        const map = {
            nouveau: ['badge-planifiee', 'Planifiée'],
            assigne: ['badge-en-cours', 'En cours'],
            rdv_planifie: ['badge-planifiee', 'Planifiée'],
            en_cours: ['badge-en-cours', 'En cours'],
            travaux_en_cours: ['badge-en-cours', 'En cours'],
            termine: ['badge-terminee', 'Terminée'],
            clos: ['badge-terminee', 'Terminée'],
        };
        const [cls, label] = map[state] || ['badge-planifiee', 'Planifiée'];
        return `<span class="badge ${cls}">${label}</span>`;
    }

    /* ── Format date ── */
    function _fmtDate(d) {
        if (!d) return '—';
        const dt = new Date(d);
        return dt.toLocaleDateString('fr-FR', { day: 'numeric', month: 'long', year: 'numeric' });
    }

    function _fmtDateTime(d) {
        if (!d) return '—';
        const dt = new Date(d);
        const today = new Date();
        const tomorrow = new Date(); tomorrow.setDate(today.getDate() + 1);
        let day = '';
        if (dt.toDateString() === today.toDateString()) day = "Aujourd'hui";
        else if (dt.toDateString() === tomorrow.toDateString()) day = 'Demain';
        else day = dt.toLocaleDateString('fr-FR', { day: 'numeric', month: 'short' });
        const time = dt.toLocaleTimeString('fr-FR', { hour: '2-digit', minute: '2-digit' });
        return `${day} · ${time}`;
    }

    /* ═══════════════════════════════════════════
       DASHBOARD (tableau de bord)
    ═══════════════════════════════════════════ */
    async function _loadDashboard() {
        try {
            const data = await API.getMissions();
            _missions = data.missions || [];
            localStorage.setItem('ss_missions_cache', JSON.stringify(_missions));
        } catch(err) {
            const cached = localStorage.getItem('ss_missions_cache');
            if (cached) {
                try { _missions = JSON.parse(cached); } catch(e) {}
            }
            console.warn('[Dashboard] API unavailable, using cache');
        }

        _updateDashStats();
        _renderToday();
        _renderCarteNext();
    }

    function _updateDashStats() {
        const ACTIVE_STATES = ['assigne','rdv_planifie','en_cours','devis_envoye','devis_accepte','travaux_en_cours','nouveau'];
        const actives = _missions.filter(m => ACTIVE_STATES.includes(m.state)).length;

        // CA depuis les données utilisateur stockées
        let user = {};
        try { user = JSON.parse(localStorage.getItem('ss_user') || '{}'); } catch(e) {}
        const caMonth = user.ca_total || 2095;
        const totalInterv = user.interventions || 487;

        var sA = document.getElementById('statActives');
        var sC = document.getElementById('statCA');
        var sN = document.getElementById('statNote');
        var sI = document.getElementById('statInterventions');
        if (sA) sA.textContent = actives || _missions.length || '—';
        if (sC) sC.textContent = caMonth.toLocaleString('fr-FR') + ' €';
        if (sN) sN.textContent = (user.note_moyenne || 4.9).toFixed(1);
        if (sI) sI.textContent = totalInterv;

        // Interventions page stats
        var sIT = document.getElementById('statIntervTotal');
        var sIC = document.getElementById('statIntervCA');
        var sIM = document.getElementById('statIntervMoyen');
        if (sIT) sIT.textContent = totalInterv;
        if (sIC) sIC.textContent = caMonth.toLocaleString('fr-FR') + ' €';
        if (sIM) sIM.textContent = totalInterv ? Math.round(caMonth / totalInterv) + ' €' : '349 €';
    }

    function _renderToday() {
        const container = document.getElementById('todayList');
        if (!container) return;

        // Missions actives (tri par urgence puis date)
        const ACTIVE_STATES = ['assigne','rdv_planifie','en_cours','devis_envoye','devis_accepte','travaux_en_cours','nouveau'];
        let items = _missions.filter(m => ACTIVE_STATES.includes(m.state));

        // Aucune mission
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
            const addr = (m.adresse_intervention || m.adresse || '');
            const city = addr.includes(',') ? addr.split(',').slice(-1)[0].trim() : addr.split(' · ').slice(-1)[0];
            const title = m.description_sinistre || m.title || '—';
            const price = m.montant || m.montant_devis || 0;
            const stateBadge = (m.urgence === 'urgente' || m.urgence === 'tres_urgente')
                ? _urgenceBadge(m.urgence)
                : _stateBadge(m.state);
            return `
                <div class="today-item" ${m.id ? `onclick="MissionDetail.open(${m.id})"` : ''}>
                    <div class="today-item-top">
                        ${_metierBadge(m.type_intervention)}
                        ${stateBadge}
                    </div>
                    <div class="today-item-title">${title}</div>
                    <div class="today-item-addr">${city}</div>
                    <div class="today-item-foot">
                        <span class="today-item-time">
                            <svg width="12" height="12" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2"><circle cx="12" cy="12" r="10"/><polyline points="12 6 12 12 16 14"/></svg>
                            ${_fmtDateTime(m.date_rdv)}
                        </span>
                        <span class="today-item-price">${price ? price.toLocaleString('fr-FR') + ' €' : '—'}</span>
                    </div>
                </div>
            `;
        }).join('');
    }

    /* ═══════════════════════════════════════════
       MISSIONS EN COURS
    ═══════════════════════════════════════════ */
    function loadMissions() {
        const container = document.getElementById('missionsList');
        if (!container) return;

        container.innerHTML = '<div class="skeleton-card-h"></div><div class="skeleton-card-h"></div>';

        const ACTIVE_STATES = ['assigne','rdv_planifie','en_cours','devis_envoye','devis_accepte','travaux_en_cours','nouveau'];
        
        // Try fresh API call
        API.getMissions().then(data => {
            _missions = data.missions || [];
            localStorage.setItem('ss_missions_cache', JSON.stringify(_missions));
        }).catch(() => {
            // use cached
        }).finally(() => {
            const missions = _missions.filter(m => ACTIVE_STATES.includes(m.state));
            var sub = document.getElementById('missionsSubtitle');
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
                const haystack = ((m.description_sinistre||'')+(m.client||'')+(m.adresse_intervention||'')).toLowerCase();
                if (!haystack.includes(q)) return false;
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
                    <div class="empty-state-sub">${isFiltered ? 'Modifiez vos filtres pour voir plus de missions' : 'Vous n\'avez pas encore de missions assignées'}</div>
                </div>`;
            return;
        }

        container.innerHTML = filtered.map(m => `
            <div class="mission-card-h">
                <div class="mc-top">
                    ${_metierBadge(m.type_intervention)}
                    ${_urgenceBadge(m.urgence)}
                    <span class="mc-ref">Réf. ${m.reference}</span>
                    <span class="mc-price">${(m.montant || m.montant_devis) ? (m.montant || m.montant_devis).toLocaleString('fr-FR') + ' €' : '—'}</span>
                    <div style="text-align:right">
                        <div style="font-size:11px;color:#9CA3AF">Client : ${m.client||'—'}</div>
                    </div>
                </div>
                <div class="mc-title">${m.description_sinistre || m.description || '—'}</div>
                <div class="mc-desc">${m.desc_detail || ''}</div>
                <div class="mc-meta">
                    <span class="mc-meta-item">
                        <svg width="13" height="13" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2"><circle cx="12" cy="10" r="3"/><path d="M12 21.7C17.3 17 20 13 20 10a8 8 0 1 0-16 0c0 3 2.7 6.9 8 11.7z"/></svg>
                        ${m.adresse_intervention || m.adresse || '—'}${m.dist ? ' · ' + m.dist : ''}
                    </span>
                    <span class="mc-meta-item">
                        <svg width="13" height="13" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2"><circle cx="12" cy="12" r="10"/><polyline points="12 6 12 12 16 14"/></svg>
                        ${_fmtDateTime(m.date_rdv)}
                    </span>
                </div>
                <div class="mc-actions">
                    <button class="btn-start" onclick="MissionDetail && MissionDetail.open(${JSON.stringify(m.id||m.reference)})">Démarrer l'intervention</button>
                    <button class="btn-nav">
                        <svg width="13" height="13" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2"><line x1="22" y1="2" x2="11" y2="13"/><polygon points="22 2 15 22 11 13 2 9 22 2"/></svg>
                        Itinéraire
                    </button>
                    <button class="btn-call">
                        <svg width="13" height="13" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2"><path d="M22 16.92v3a2 2 0 0 1-2.18 2 19.79 19.79 0 0 1-8.63-3.07A19.5 19.5 0 0 1 4.69 13.5 19.79 19.79 0 0 1 1.6 4.86C1.6 3.82 2.4 3 3.44 3h3a2 2 0 0 1 2 1.72c.127.96.361 1.903.7 2.81a2 2 0 0 1-.45 2.11L7.91 10.4a16 16 0 0 0 6 6l.78-.78a2 2 0 0 1 2.11-.45c.907.339 1.85.573 2.81.7A2 2 0 0 1 21.28 18z"/></svg>
                        Appeler client
                    </button>
                </div>
            </div>
        `).join('');
    }

    /* ═══════════════════════════════════════════
       INTERVENTIONS RÉALISÉES
    ═══════════════════════════════════════════ */
    function loadInterventions() {
        const demo = [
            { ref: 'M-2026-0455', date: '2026-05-22', client: 'M. Roux',          type: 'serrurerie',  prestation: 'Changement cylindre',   addr: '15 rue du Faubourg',      montant: 240 },
            { ref: 'M-2026-0452', date: '2026-05-20', client: 'Mme Aziz',         type: 'plomberie',   prestation: 'Débouchage canalisation', addr: '9 rue Saint-Maur',        montant: 165 },
            { ref: 'M-2026-0448', date: '2026-05-18', client: 'Boulangerie Paul',  type: 'electricite', prestation: 'Réparation four pro',     addr: '31 av. de la République', montant: 380 },
            { ref: 'M-2026-0444', date: '2026-05-15', client: 'M. Garnier',        type: 'plomberie',   prestation: 'Entretien annuel chaudière', addr: '4 rue Popincourt',     montant: 130 },
            { ref: 'M-2026-0440', date: '2026-05-12', client: 'Mme Lefèvre',       type: 'vitrerie',    prestation: 'Pose miroir sur mesure',  addr: '18 rue Crussol',          montant: 290 },
            { ref: 'M-2026-0437', date: '2026-05-08', client: 'M. Nguyen',         type: 'serrurerie',  prestation: 'Blindage porte palière',  addr: '62 rue de Charonne',      montant: 890 },
        ];

        // Merge avec missions terminées de l'API
        const apiTerminees = _missions
            .filter(m => m.state === 'termine' || m.state === 'clos')
            .map(m => ({
                ref: m.reference, date: m.date_cloture, client: m.client,
                type: m.type_intervention, prestation: m.description_sinistre,
                addr: m.adresse_intervention, montant: m.montant,
            }));

        _interventions = apiTerminees;
        _renderInterventions();

        // Update stats
        const total = _interventions.length;
        const ca = _interventions.reduce((a, i) => a + (i.montant || 0), 0);
        var sIT = document.getElementById('statIntervTotal');
        var sIC = document.getElementById('statIntervCA');
        var sIM = document.getElementById('statIntervMoyen');
        if (sIT) sIT.textContent = total;
        if (sIC) sIC.textContent = ca.toLocaleString('fr-FR') + ' €';
        if (sIM) sIM.textContent = total ? Math.round(ca / total).toLocaleString('fr-FR') + ' €' : '—';
    }

    function _renderInterventions() {
        const tbody = document.getElementById('intervTableBody');
        if (!tbody) return;

        let list = _intervFilter === 'all'
            ? _interventions
            : _interventions.filter(i => i.type === _intervFilter);

        if (!list.length) {
            tbody.innerHTML = `
                <tr><td colspan="7">
                    <div class="empty-state-full" style="padding:60px 0">
                        <div class="empty-state-icon">✅</div>
                        <div class="empty-state-title">Aucune intervention terminée</div>
                        <div class="empty-state-sub">Vos interventions réalisées apparaîtront ici</div>
                    </div>
                </td></tr>`;
            return;
        }

        tbody.innerHTML = list.map(i => `
            <tr>
                <td class="interv-ref">${i.ref}</td>
                <td class="interv-date">
                    <svg width="13" height="13" viewBox="0 0 24 24" fill="none" stroke="#9CA3AF" stroke-width="2"><rect x="3" y="4" width="18" height="18" rx="2"/><line x1="16" y1="2" x2="16" y2="6"/><line x1="8" y1="2" x2="8" y2="6"/><line x1="3" y1="10" x2="21" y2="10"/></svg>
                    ${_fmtDate(i.date)}
                </td>
                <td>${i.client || '—'}</td>
                <td>${_metierBadge(i.type)}</td>
                <td>
                    <div style="font-weight:600;font-size:13.5px">${i.prestation || '—'}</div>
                    <div style="font-size:12px;color:#9CA3AF">${i.addr || ''}</div>
                </td>
                <td class="interv-amount">${i.montant ? i.montant + ' €' : '—'}</td>
                <td><span class="badge badge-terminee">Terminée</span></td>
            </tr>
        `).join('');
    }

    /* ═══════════════════════════════════════════
       CARTE
    ═══════════════════════════════════════════ */
    function initCarte() {
        _renderCarteNext();
    }

    function _renderCarteNext() {
        // Prendre la première mission active
        const ACTIVE = ['assigne','rdv_planifie','en_cours','devis_envoye','devis_accepte','travaux_en_cours','nouveau'];
        const first = _missions.find(m => ACTIVE.includes(m.state));
        var ct = document.getElementById('carteNextTitle');
        var ca = document.getElementById('carteNextAddr');
        var cd = document.getElementById('carteNextDist');
        var cp = document.getElementById('carteNextPrice');
        if (!first) {
            if (ct) ct.textContent = 'Aucune mission';
            if (ca) ca.textContent = '—';
            if (cd) cd.textContent = '—';
            if (cp) cp.textContent = '—';
            return;
        }
        if (ct) ct.textContent = first.description_sinistre || first.description || '—';
        if (ca) ca.textContent = first.adresse_intervention || first.adresse || '—';
        if (cd) cd.textContent = '—';
        if (cp) cp.textContent = first.montant ? first.montant + ' €' : '—';
    }

    function showMapPin(idx) {
        const pin = MAP_PINS[idx];
        if (!pin) return;
        _currentMapPin = idx;

        // Dashboard popup
        var popup = document.getElementById('mapPopup');
        if (popup) {
            document.getElementById('mapPopupBadges').innerHTML = _metierBadge(pin.type) + (pin.urgence ? _urgenceBadge(pin.urgence) : '');
            document.getElementById('mapPopupTitle').textContent = pin.title;
            document.getElementById('mapPopupAddr').textContent = pin.addr;
            document.getElementById('mapPopupPrice').innerHTML = `<span style="font-size:18px;font-weight:800;color:#1E40AF">${pin.price}</span> <span style="font-size:12px;color:#6B7280">${pin.dist}</span>`;
            popup.style.display = 'block';
        }

        // Carte popup
        var cp = document.getElementById('carteMapPopup');
        if (cp) {
            document.getElementById('cartePopupBadges').innerHTML = _metierBadge(pin.type) + (pin.urgence ? _urgenceBadge(pin.urgence) : '');
            document.getElementById('cartePopupTitle').textContent = pin.title;
            document.getElementById('cartePopupAddr').textContent = pin.addr;
            document.getElementById('cartePopupPrice').innerHTML = `<span style="font-size:18px;font-weight:800;color:#1E40AF">${pin.price}</span> <span style="font-size:12px;color:#6B7280">${pin.dist}</span>`;
            cp.style.display = 'block';
        }
    }

    function acceptMission() {
        Toast.show('Mission acceptée ! 🎉', 'success');
        var popup = document.getElementById('mapPopup');
        if (popup) popup.style.display = 'none';
    }

    /* ═══════════════════════════════════════════
       FILTRES
    ═══════════════════════════════════════════ */
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
        _searchQuery = (document.getElementById('missionsSearch') || {}).value || '';
        _renderMissions(_missions.filter(m => ['assigne','rdv_planifie','en_cours','devis_envoye','devis_accepte','travaux_en_cours','nouveau'].includes(m.state)));
    }

    /* ── API publique ── */
    return {
        init() { _loadDashboard(); },
        loadMissions,
        loadInterventions,
        initCarte,
        showMapPin,
        acceptMission,
        setMetierFilter,
        setStatusFilter,
        setIntervFilter,
        filterMissions,
        // Legacy compat
        setFilter(f, btn) {},
        refresh() { _loadDashboard(); },
    };
})();
