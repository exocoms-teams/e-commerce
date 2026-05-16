/**
 * dashboard.js — Écran principal : liste des missions
 */

window.Dashboard = (() => {
    let _missions = [];
    let _filter   = 'all';
    let _isLoading = false;
    let _pullStartY = 0;

    /* ── Chargement ── */
    async function load(showSkeleton = true) {
        if (_isLoading) return;
        _isLoading = true;

        if (showSkeleton) {
            document.getElementById('skeletonList').style.display = 'flex';
            document.getElementById('missionList').style.display  = 'none';
        }

        try {
            const data = await API.getMissions();
            _missions  = data.missions || [];
            _updateStats();
            _renderList();
        } catch (err) {
            if (err.message !== 'OFFLINE') {
                Toast.show('Erreur chargement: ' + err.message, 'error');
            }
            // En offline : afficher depuis cache si dispo
            const cached = localStorage.getItem('ss_missions_cache');
            if (cached) {
                _missions = JSON.parse(cached);
                _renderList();
                Toast.show('📡 Données en cache (hors ligne)', 'warning');
            }
        } finally {
            _isLoading = false;
            document.getElementById('skeletonList').style.display = 'none';
            document.getElementById('missionList').style.display  = 'flex';
        }
    }

    function _updateStats() {
        const now = new Date();
        const thisMonth = now.getMonth();

        const nouveau  = _missions.filter(m => m.state === 'nouveau').length;
        const urgent   = _missions.filter(m => m.urgence === 'tres_urgente' || m.urgence === 'urgente').length;
        const termine  = _missions.filter(m => {
            if (m.state !== 'termine' && m.state !== 'clos') return false;
            if (!m.date_cloture) return false;
            return new Date(m.date_cloture).getMonth() === thisMonth;
        }).length;

        document.getElementById('statNouveau').textContent = nouveau;
        document.getElementById('statUrgent').textContent  = urgent;
        document.getElementById('statTermine').textContent = termine;

        // Cache pour offline
        localStorage.setItem('ss_missions_cache', JSON.stringify(_missions));
    }

    function _filtered() {
        if (_filter === 'all') return _missions;
        if (_filter === 'en_cours') {
            return _missions.filter(m =>
                ['assigne','rdv_planifie','en_cours','devis_envoye','devis_accepte','travaux_en_cours'].includes(m.state)
            );
        }
        return _missions.filter(m => m.state === _filter);
    }

    function _renderList() {
        const container = document.getElementById('missionList');
        const empty     = document.getElementById('emptyState');
        const missions  = _filtered();

        if (!missions.length) {
            empty.style.display = 'flex';
            container.innerHTML = '';
            container.appendChild(empty);
            return;
        }

        empty.style.display = 'none';
        container.innerHTML = '';

        missions.forEach(m => {
            container.appendChild(_buildCard(m));
        });
    }

    function _buildCard(m) {
        const card = document.createElement('div');
        const urgenceClass = m.urgence === 'tres_urgente' ? 'tres_urgente' : m.urgence === 'urgente' ? 'urgente' : '';
        card.className = `mission-card ${urgenceClass}`;

        const state = CONFIG.STATE_LABELS[m.state] || { label: m.state, icon: '❓', css: 'state-default' };
        const urgConf = CONFIG.URGENCE_COLORS[m.urgence] || CONFIG.URGENCE_COLORS.normale;
        const typeLabel = CONFIG.TYPE_LABELS[m.type_intervention] || m.type_intervention;

        const rdvStr = m.date_rdv
            ? `RDV : ${new Date(m.date_rdv).toLocaleDateString('fr-FR', { weekday:'short', day:'numeric', month:'short', hour:'2-digit', minute:'2-digit' })}`
            : '';

        card.innerHTML = `
            <div class="mission-card-head">
                <span class="mission-ref">${m.reference}</span>
                <span class="mission-urgence-badge urgence-${m.urgence}"
                      style="background:${urgConf.bg};color:${urgConf.text}">
                    ${urgConf.icon} ${m.urgence === 'tres_urgente' ? 'Très urgent' : m.urgence === 'urgente' ? 'Urgent' : 'Normal'}
                </span>
            </div>
            <div class="mission-type">${typeLabel}</div>
            <div class="mission-client">👤 ${m.client || ''}</div>
            <div class="mission-adresse">📍 ${m.adresse || ''}</div>
            <div class="mission-card-foot">
                <span class="mission-state-badge ${state.css}">${state.icon} ${state.label}</span>
                <span class="mission-rdv">${rdvStr}</span>
            </div>
        `;

        card.addEventListener('click', () => MissionDetail.open(m.id || m.reference));
        _addRipple(card);

        return card;
    }

    function _addRipple(el) {
        el.style.position = 'relative';
        el.style.overflow = 'hidden';
        el.addEventListener('click', (e) => {
            const rect   = el.getBoundingClientRect();
            const ripple = document.createElement('span');
            const size   = Math.max(rect.width, rect.height);
            ripple.className = 'ripple';
            ripple.style.cssText = `
                width:${size}px; height:${size}px;
                left:${e.clientX - rect.left - size/2}px;
                top:${e.clientY - rect.top - size/2}px;
            `;
            el.appendChild(ripple);
            setTimeout(() => ripple.remove(), 700);
        });
    }

    /* ── Pull-to-refresh ── */
    function _initPullToRefresh() {
        const scrollEl = document.querySelector('.view-scroll');
        if (!scrollEl) return;

        scrollEl.addEventListener('touchstart', (e) => {
            if (scrollEl.scrollTop === 0) _pullStartY = e.touches[0].clientY;
        }, { passive: true });

        scrollEl.addEventListener('touchmove', (e) => {
            if (!_pullStartY) return;
            const delta = e.touches[0].clientY - _pullStartY;
            if (delta > 60) {
                document.getElementById('refreshZone').classList.add('active');
            }
        }, { passive: true });

        scrollEl.addEventListener('touchend', () => {
            const zone = document.getElementById('refreshZone');
            if (zone.classList.contains('active')) {
                zone.classList.remove('active');
                load(false);
                Toast.show('Actualisation…');
            }
            _pullStartY = 0;
        }, { passive: true });
    }

    /* ── API publique ── */
    return {
        init() {
            load();
            _initPullToRefresh();
        },

        refresh() { load(false); },

        setFilter(filter, btn) {
            _filter = filter;
            document.querySelectorAll('.filter-btn').forEach(b => b.classList.remove('active'));
            btn.classList.add('active');
            _renderList();
        },
    };
})();
