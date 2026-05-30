/**
 * app.js — Orchestrateur principal de la PWA
 * Gère : démarrage, routing, navigation, Service Worker
 */

window.App = (() => {
    let _history     = [];          // pile de navigation
    let _currentView = 'dashboard';

    /* ── Démarrage ── */
    async function init() {
    await _registerSW();
    await _sleep(1400);

    // 1. Vérifier session localStorage existante
    const user = Auth.loadFromStorage();
    if (user) {
        const valid = await Auth.verify().catch(() => false);
        if (valid) { await _enrichUserFromAPI(); showApp(); return; }
    }

    // 2. Vérifier session Odoo cookie (venant de /intervenant/login)
    try {
        const resp = await fetch('/web/session/get_session_info', {
            method: 'POST',
            credentials: 'include',
            headers: { 'Content-Type': 'application/json' },
            body: JSON.stringify({ jsonrpc: '2.0', method: 'call', params: {} })
        });
        const data = await resp.json();
        if (data.result && data.result.uid > 0) {
            // Session Odoo valide — sauvegarder et afficher l'app
            const u = {
                uid:   data.result.uid,
                name:  data.result.name,
                email: data.result.username,
                lang:  data.result.lang,
            };
            localStorage.setItem('ss_user', JSON.stringify(u));
            Auth.loadFromStorage();
            await _enrichUserFromAPI();
            showApp();
            return;
        }
    } catch(e) {}

    // 3. Aucune session → afficher login
    showLogin();
}


    /* ── Mettre à jour les certifications ── */
    function _updateCertifications(certifs) {
        const list = document.getElementById('certifList');
        if (!list) return;
        if (!certifs || !certifs.length) {
            list.innerHTML = '<p style="color:#9CA3AF;font-size:13px;padding:8px 0">Aucune certification renseignée</p>';
            return;
        }
        const icons = [
            '<svg width="18" height="18" viewBox="0 0 24 24" fill="none" stroke="#10B981" stroke-width="2"><path d="M12 22s8-4 8-10V5l-8-3-8 3v7c0 6 8 10 8 10z"/></svg>',
            '<svg width="18" height="18" viewBox="0 0 24 24" fill="none" stroke="#10B981" stroke-width="2"><circle cx="12" cy="8" r="6"/><path d="M15.477 12.89 17 22l-5-3-5 3 1.523-9.11"/></svg>',
            '<svg width="18" height="18" viewBox="0 0 24 24" fill="none" stroke="#10B981" stroke-width="2"><path d="M14 2H6a2 2 0 0 0-2 2v16a2 2 0 0 0 2 2h12a2 2 0 0 0 2-2V8z"/><polyline points="14 2 14 8 20 8"/></svg>',
        ];
        list.innerHTML = certifs.map((cert, i) => `
            <div class="certif-item">
                ${icons[i % icons.length]}
                <div><div class="certif-name">${cert.name}</div>${cert.date ? `<div class="certif-date">${cert.date}</div>` : ''}</div>
            </div>`).join('');
    }

    /* ── Enrichir depuis /api/sinistre/v1/me ── */
    async function _enrichUserFromAPI() {
        try {
            const resp = await fetch('/api/sinistre/v1/me', { credentials: 'include' });
            if (!resp.ok) return;
            const data = await resp.json();
            if (data.success && data.user) {
                const u = data.user;
                const existing = JSON.parse(localStorage.getItem('ss_user') || '{}');
                const merged = {
                    ...existing,
                    uid: u.uid, name: u.name, email: u.email,
                    phone: u.phone || '',
                    company_name: u.company_name || u.name,
                    zone: u.zone || '',
                    note_moyenne: u.note_moyenne || 0,
                    interventions: u.interventions || 0,
                    ca_total: u.ca_total || 0,
                    ca_mois: u.ca_mois || 0,
                    specialites: u.specialites || [],
                    specialites_types: u.specialites_types || [],
                    membre_depuis: u.membre_depuis || '',
                    certifications: u.certifications || [],
                    intervenant_id: u.intervenant_id,
                };
                localStorage.setItem('ss_user', JSON.stringify(merged));
                Auth.loadFromStorage();
                _updateUIFromUser();
                if (merged.certifications.length) _updateCertifications(merged.certifications);
            }
        } catch(e) { console.warn('[App] enrichUser:', e); }
    }

    /* ── Mettre à jour l'UI ── */
    function _updateUIFromUser() {
        let user = null;
        try { user = JSON.parse(localStorage.getItem('ss_user') || '{}'); } catch(e) {}
        if (!user || !user.name) return;

        const name = user.name || '';
        const parts = name.split(' ');
        const first = parts[0] || '';
        const initials = parts.map(w => w[0] || '').join('').substring(0, 2).toUpperCase();
        const company = user.company_name || name;
        const nbInterv = user.interventions || 0;
        const note = nbInterv > 0 ? (user.note_moyenne || 0) : 0;
        const caMois = user.ca_mois || 0;

        const set = (id, val) => { const el = document.getElementById(id); if (el) el.textContent = val; };
        const setVal = (id, val) => { const el = document.getElementById(id); if (el) el.value = val; };

        // Greeting + sidebar
        set('dashGreeting', `Bonjour ${first} 👋`);
        set('sidebarAvatar', initials || '?');
        set('sidebarName', name);
        set('sidebarCompany', company);

        // Stats dashboard
        const sA = document.getElementById('statActives');
        if (sA && sA.textContent === '–') sA.textContent = '0';
        const sC = document.getElementById('statCA');
        if (sC) sC.textContent = caMois.toLocaleString('fr-FR') + ' €';
        set('statNote', nbInterv > 0 ? note.toFixed(1) : '0');
        set('statInterventions', nbInterv);

        // Profil
        set('profileAvatarLg', initials || '?');
        set('profileNameLg', name);
        set('profileCompanyLg', company);
        set('profileRating', nbInterv > 0 ? note.toFixed(1) : '0');
        set('profileInterv', nbInterv);
        set('profileSince', user.membre_depuis || '—');
        setVal('profileEmail', user.email || '');
        setVal('profileTel', user.phone || '');
        setVal('profileZone', user.zone || '');
        setVal('profileEntreprise', company);

        // Spécialités
        const specs = user.specialites || [];
        const sTypes = user.specialites_types || [];
        const ptags = document.getElementById('profileMetiersTags');
        if (ptags) ptags.innerHTML = specs.length
            ? specs.map(s => `<span class="metier-tag">${s}</span>`).join('')
            : '<span style="color:#9CA3AF;font-size:12px">Aucune spécialité renseignée</span>';

        document.querySelectorAll('.metier-check').forEach(label => {
            const cb = label.querySelector('input[type="checkbox"]');
            const text = label.textContent.trim().toLowerCase();
            const map = { serrurerie:['serrurerie'], plomberie:['plomberie'], 'électricité':['electricite'], electricite:['electricite'], menuiserie:['menuiserie_int','menuiserie_ext'], vitrerie:['vitrerie'] };
            const matched = Object.keys(map).some(k => text.includes(k) && (sTypes.some(t => map[k].includes(t)) || specs.some(s => s.toLowerCase().includes(k))));
            if (cb) cb.checked = matched;
            label.classList.toggle('active', matched);
        });

        // Certifications
        if (user.certifications && user.certifications.length) _updateCertifications(user.certifications);
    }

    async function _registerSW() {
        if (!('serviceWorker' in navigator)) return;
        try {
            const reg = await navigator.serviceWorker.register(CONFIG.SW_PATH, { scope: '/sinistre_services/static/pwa/' });
            console.log('[SW] Enregistré:', reg.scope);

            // Écouter les messages du SW
            navigator.serviceWorker.addEventListener('message', (e) => {
                if (e.data?.type === 'OPEN_MISSION') {
                    MissionDetail.open(e.data.missionId);
                }
            });
        } catch (err) {
            console.warn('[SW] Erreur enregistrement:', err);
        }
    }
    
    function showLogin() {
        _hideSplash();
        // Rediriger vers la page login Odoo au lieu d'afficher l'écran PWA
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

        // Deep link : ouvrir une mission depuis push
        const urlParams = new URLSearchParams(window.location.search);
        const missionId = urlParams.get('mission');
        if (missionId) {
            MissionDetail.open(missionId);
        }

        // Rejouer queue offline si en ligne
        if (Offline.isOnline()) Offline.processQueue();

        // Nom dashboard
        const u = Auth.getUser();
        if (u && u.name) {
            const el = document.getElementById('dashWelcome');
            if (el) el.textContent = 'Bonjour, ' + u.name.split(' ')[0] + ' !';
        }
    }

    function _hideSplash() {
        const splash = document.getElementById('splash');
        splash.classList.add('hidden');
        setTimeout(() => { splash.style.display = 'none'; }, 400);
        document.getElementById('app').style.display = 'flex';
    }

    /* ── Navigation entre vues ── */
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
        if (viewId === 'dashboard')     Dashboard.init();
        if (viewId === 'profile')       setTimeout(_updateUIFromUser, 100);
        if (viewId === 'missions')      Dashboard.loadMissions();
        if (viewId === 'interventions') Dashboard.loadInterventions();
        if (viewId === 'carte') {
            requestAnimationFrame(() => {
                requestAnimationFrame(() => {
                    if (window.CarteMap) CarteMap.init();
                });
            });
        }
    }

    function goBack() {
        const prev = _history.pop() || 'dashboard';
        _currentView = 'dashboard';
        showView(prev, document.getElementById('nav-' + prev));
    }

    /* ── Utilitaires ── */
    function _sleep(ms) { return new Promise(r => setTimeout(r, ms)); }

    /* ── Gestionnaire install PWA ── */
    let _deferredPrompt = null;
    window.addEventListener('beforeinstallprompt', (e) => {
        e.preventDefault();
        _deferredPrompt = e;
        // On pourrait afficher un bouton "Installer l'app" ici
    });

    /* ── Back button Android ── */
    window.addEventListener('popstate', () => {
        if (_history.length) goBack();
    });

    /* ── Visibility change (rafraîchir si retour en premier plan) ── */
    document.addEventListener('visibilitychange', () => {
        if (!document.hidden && Auth.isLoggedIn() && _currentView === 'dashboard') {
            Dashboard.refresh();
        }
    });

    /* ── Start ── */
    if (document.readyState === 'loading') {
        document.addEventListener('DOMContentLoaded', init);
    } else {
        init();
    }

    return {
        showLogin,
        showApp,
        showView,
        goBack,
        get currentView() { return _currentView; },
    };
})();
