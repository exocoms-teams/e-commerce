/**
 * app.js — Orchestrateur principal de la PWA ArtisanPro
 */

window.App = (() => {
    let _history     = [];
    let _currentView = 'dashboard';

    /* ── Démarrage ── */
    async function init() {
        await _registerSW();
        await _sleep(1400);

        // 1. Session localStorage existante ?
        const cached = Auth.loadFromStorage();
        if (cached) {
            const valid = await Auth.verify().catch(() => false);
            if (valid) {
                await _enrichUserFromAPI();
                showApp();
                return;
            }
        }

        // 2. Session Odoo cookie ?
        try {
            const resp = await fetch('/web/session/get_session_info', {
                method: 'POST',
                credentials: 'include',
                headers: { 'Content-Type': 'application/json' },
                body: JSON.stringify({ jsonrpc: '2.0', method: 'call', params: {} })
            });
            const data = await resp.json();
            if (data.result && data.result.uid > 0) {
                const u = {
                    uid:   data.result.uid,
                    name:  data.result.name,
                    email: data.result.username,
                    lang:  data.result.lang,
                };
                localStorage.setItem('ss_user', JSON.stringify(u));
                Auth.loadFromStorage();
                // Enrichir avec les données intervenant
                await _enrichUserFromAPI();
                showApp();
                return;
            }
        } catch(e) {}

        showLogin();
    }

    /* ── Enrichir l'utilisateur depuis /api/sinistre/v1/me ── */
    async function _enrichUserFromAPI() {
        try {
            const resp = await fetch('/api/sinistre/v1/me', {
                credentials: 'include',
                headers: { 'Content-Type': 'application/json' }
            });
            if (!resp.ok) return;
            const data = await resp.json();
            if (data.success && data.user) {
                const u = data.user;
                // Fusionner avec le stockage existant
                const existing = JSON.parse(localStorage.getItem('ss_user') || '{}');
                const merged = {
                    ...existing,
                    uid:           u.uid,
                    name:          u.name,
                    email:         u.email,
                    company_name:  u.company_name,
                    zone:          u.zone,
                    note_moyenne:  u.note_moyenne,
                    interventions: u.interventions,
                    ca_total:      u.ca_total,
                    intervenant_id: u.intervenant_id,
                };
                localStorage.setItem('ss_user', JSON.stringify(merged));
                Auth.loadFromStorage();
            }
        } catch(e) {
            console.warn('[App] enrichUser failed:', e);
        }
    }

    async function _registerSW() {
        if (!('serviceWorker' in navigator)) return;
        try {
            const reg = await navigator.serviceWorker.register(CONFIG.SW_PATH, {
                scope: '/sinistre_services/static/pwa/'
            });
            console.log('[SW] Enregistré:', reg.scope);
            navigator.serviceWorker.addEventListener('message', (e) => {
                if (e.data?.type === 'OPEN_MISSION') {
                    MissionDetail.open(e.data.missionId);
                }
            });
        } catch (err) {
            console.warn('[SW] Erreur:', err);
        }
    }

    function showLogin() {
        _hideSplash();
        window.location.href = '/intervenant/login';
    }

    function showApp() {
        _hideSplash();
        const sl = document.getElementById('screen-login');
        const sa = document.getElementById('screen-app');
        if (sl) sl.style.display = 'none';
        if (sa) sa.style.display = 'flex';
        FCM.autoInit();
        _updateUIFromUser();
        showView('dashboard', document.getElementById('nav-dashboard'));
    }

    /* ── Mettre à jour l'UI avec les données utilisateur ── */
    function _updateUIFromUser() {
        let user = null;
        try { user = JSON.parse(localStorage.getItem('ss_user') || '{}'); } catch(e) {}
        if (!user || !user.name) return;

        const name     = user.name || '';
        const parts    = name.split(' ');
        const first    = parts[0] || '';
        const initials = parts.map(w => w[0] || '').join('').substring(0, 2).toUpperCase();
        const company  = user.company_name || name;

        // Greeting dashboard
        const dg = document.getElementById('dashGreeting');
        if (dg) dg.textContent = `Bonjour ${first} 👋`;

        // Sidebar
        const sa = document.getElementById('sidebarAvatar');
        const sn = document.getElementById('sidebarName');
        const sc = document.getElementById('sidebarCompany');
        if (sa) sa.textContent = initials || '?';
        if (sn) sn.textContent = name;
        if (sc) sc.textContent = company;

        // Stats dashboard
        const sN  = document.getElementById('statNote');
        const sI  = document.getElementById('statInterventions');
        const sCA = document.getElementById('statCA');
        const nbInterv = user.interventions || 0;
        const note = nbInterv > 0 ? (user.note_moyenne || 0) : 0;
        const caMois = user.ca_mois || 0;
        if (sN)  sN.textContent  = nbInterv > 0 ? note.toFixed(1) : '0';
        if (sI)  sI.textContent  = nbInterv;
        if (sCA) sCA.textContent = caMois.toLocaleString('fr-FR') + ' €';

        // ── Page profil ──
        const pa = document.getElementById('profileAvatarLg');
        const pn = document.getElementById('profileNameLg');
        const pc = document.getElementById('profileCompanyLg');
        const pe = document.getElementById('profileEmail');
        const pt = document.getElementById('profileTel');
        const pz = document.getElementById('profileZone');
        const pe2 = document.getElementById('profileEntreprise');
        if (pa)  pa.textContent = initials || '?';
        if (pn)  pn.textContent = name;
        if (pc)  pc.textContent = company;
        if (pe)  pe.value       = user.email || '';
        if (pt)  pt.value       = user.phone || '';
        if (pz)  pz.value       = user.zone  || '';
        if (pe2) pe2.value      = company;

        // Note et interventions sur la page profil
        const pr  = document.getElementById('profileRating');
        const pi  = document.getElementById('profileInterv');
        const ps  = document.getElementById('profileSince');
        if (pr) pr.textContent = nbInterv > 0 ? note.toFixed(1) : '0';
        if (pi) pi.textContent = nbInterv;
        if (ps) ps.textContent = user.membre_depuis || '—';

        // Spécialités sur la page profil
        const ptags = document.getElementById('profileMetiersTags');
        if (ptags && user.specialites && user.specialites.length) {
            ptags.innerHTML = user.specialites
                .map(s => `<span class="metier-tag">${s}</span>`)
                .join('');
        } else if (ptags) {
            ptags.innerHTML = '<span style="color:#9CA3AF;font-size:12px">Aucune spécialité renseignée</span>';
        }

        // Rating badge profil (0/5 si aucune intervention)
        const ratingBadge = document.querySelector('.profile-rating');
        if (ratingBadge) {
            ratingBadge.innerHTML = `<span>⭐</span> <span id="profileRating">${nbInterv > 0 ? note.toFixed(1) : '0'}</span> / 5`;
        }
    }

    function _hideSplash() {
        const splash = document.getElementById('splash');
        if (!splash) return;
        splash.classList.add('hidden');
        setTimeout(() => { splash.style.display = 'none'; }, 400);
        const appEl = document.getElementById('app');
        if (appEl) appEl.style.display = 'flex';
    }

    /* ── Navigation ── */
    function showView(viewId, navEl) {
        // Masquer toutes les vues
        document.querySelectorAll('.view-page').forEach(v => v.classList.remove('active'));
        const target = document.getElementById('view-' + viewId);
        if (target) target.classList.add('active');

        // Sidebar nav
        document.querySelectorAll('.sidebar-item').forEach(b => b.classList.remove('active'));
        if (navEl && navEl.classList) navEl.classList.add('active');

        _history.push(_currentView);
        _currentView = viewId;

        // Charger les données de la vue
        if (viewId === 'dashboard')      Dashboard.init();
        if (viewId === 'missions')       Dashboard.loadMissions();
        if (viewId === 'interventions')  Dashboard.loadInterventions();
        if (viewId === 'carte')          Dashboard.initCarte();
    }

    function goBack() {
        const prev = _history.pop() || 'dashboard';
        _currentView = 'dashboard';
        showView(prev, document.getElementById('nav-' + prev));
    }

    function _sleep(ms) { return new Promise(r => setTimeout(r, ms)); }

    /* ── Visibilité ── */
    document.addEventListener('visibilitychange', () => {
        if (!document.hidden && Auth.isLoggedIn() && _currentView === 'dashboard') {
            Dashboard.refresh();
        }
    });

    if (document.readyState === 'loading') {
        document.addEventListener('DOMContentLoaded', init);
    } else {
        init();
    }

    return { showLogin, showApp, showView, goBack, get currentView() { return _currentView; } };
})();
