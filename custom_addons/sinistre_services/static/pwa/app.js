/**
 * app.js — Orchestrateur principal de la PWA
 * Gère : démarrage, routing, navigation, Service Worker
 */

window.App = (() => {
    let _history     = [];          // pile de navigation
    let _currentView = 'dashboard';

    /* ── Démarrage ── */
    async function init() {
        // Enregistrer le Service Worker
        await _registerSW();

        // Animation splash
        await _sleep(1400);

        // Vérifier session
        const user = Auth.loadFromStorage();
        if (user) {
            const valid = await Auth.verify().catch(() => false);
            if (valid) {
                showApp();
                return;
            }
        }

        // Pas de session valide
        showLogin();
    }

    async function _registerSW() {
        if (!('serviceWorker' in navigator)) return;
        try {
            const reg = await navigator.serviceWorker.register(CONFIG.SW_PATH, { scope: '/pwa/' });
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

    /* ── Auth screens ── */
    function showLogin() {
        _hideSplash();
        document.getElementById('screen-login').style.display = 'flex';
        document.getElementById('screen-app').style.display   = 'none';
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
    }

    function _hideSplash() {
        const splash = document.getElementById('splash');
        splash.classList.add('hidden');
        setTimeout(() => { splash.style.display = 'none'; }, 400);
        document.getElementById('app').style.display = 'flex';
    }

    /* ── Navigation entre vues ── */
    function showView(viewId, title = '') {
        // Masquer la vue courante
        const current = document.getElementById(`view-${_currentView}`);
        if (current) current.style.display = 'none';

        // Empiler la navigation (sauf si retour au dashboard)
        if (_currentView !== viewId) {
            _history.push(_currentView);
        }
        _currentView = viewId;

        // Afficher la nouvelle vue
        const target = document.getElementById(`view-${viewId}`);
        if (target) {
            target.style.display  = 'flex';
            target.style.flexDirection = 'column';
            // Remonter en haut
            const scroll = target.querySelector('.view-scroll');
            if (scroll) scroll.scrollTop = 0;
        }

        // Titre
        if (title) document.getElementById('topbarTitle').textContent = title;

        // Bouton retour
        const backBtn = document.getElementById('backBtn');
        backBtn.style.display = (_history.length > 0 && viewId !== 'dashboard') ? 'flex' : 'none';

        // Bottom nav active
        document.querySelectorAll('.bottomnav-item').forEach(btn => btn.classList.remove('active'));
        const activeNav = document.getElementById(`nav-${viewId}`);
        if (activeNav) activeNav.classList.add('active');
        else if (viewId === 'dashboard') {
            document.getElementById('nav-dashboard').classList.add('active');
        }
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
