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
        if (valid) { showApp(); return; }
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
            showApp();
            return;
        }
    } catch(e) {}

    // 3. Aucune session → afficher login
    showLogin();
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
        document.getElementById('screen-login').style.display = 'none';
        document.getElementById('screen-app').style.display   = 'flex';
        FCM.autoInit();
        Dashboard.init();

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
    function showView(viewId, title = '') {
        // Desktop: use class-based view switching
        document.querySelectorAll('.view-page').forEach(v => v.classList.remove('active'));
        const target = document.getElementById('view-' + viewId);
        if (target) target.classList.add('active');

        // Mobile legacy fallback
        const current = document.getElementById('view-' + _currentView);
        if (current && current.classList.contains('view')) { current.style.display = 'none'; }
        if (_currentView !== viewId) { _history.push(_currentView); }
        _currentView = viewId;

        // Sidebar nav active
        document.querySelectorAll('.sidebar-item').forEach(b => b.classList.remove('active'));
        const activeNav = document.getElementById('nav-' + viewId);
        if (activeNav) activeNav.classList.add('active');

        // Optional elements
        const titleEl = document.getElementById('topbarTitle');
        if (title && titleEl) titleEl.textContent = title;
        const backBtn = document.getElementById('backBtn');
        if (backBtn) backBtn.style.display = (_history.length > 0 && viewId !== 'dashboard') ? 'flex' : 'none';

        // Load data
        if (viewId === 'dashboard') Dashboard.init();
        if (viewId === 'missions') Dashboard.loadMissions();
        if (viewId === 'interventions') Dashboard.loadInterventions();
        if (viewId === 'carte') Dashboard.initCarte();
    }

    function goBack() {
        if (!_history.length) return;
        const prev = _history.pop();
        _currentView = 'dashboard'; // pour éviter double push
        showView(prev);
        if (prev === 'dashboard') {
            document.getElementById('topbarTitle').textContent = 'Mes Missions';
        }
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
