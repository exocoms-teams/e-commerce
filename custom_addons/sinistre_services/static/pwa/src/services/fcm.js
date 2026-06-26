/**
 * fcm.js — Firebase Cloud Messaging
 * Initialise Firebase, gère la permission, reçoit les push en foreground
 */

window.FCM = (() => {
    let _messaging = null;
    let _token = null;
    let _initialized = false;
    let _panelOpen = false;
    const STORAGE_KEY = 'ss_notifications';

    function _loadNotifications() {
        try { return JSON.parse(localStorage.getItem(STORAGE_KEY) || '[]'); }
        catch (e) { return []; }
    }

    function _saveNotifications(list) {
        localStorage.setItem(STORAGE_KEY, JSON.stringify(list.slice(0, 50)));
    }

    function _updateDot() {
        const nd = document.getElementById('notifDot');
        if (!nd) return;
        const unread = _loadNotifications().filter(n => !n.read).length;
        const needsPermission = Notification.permission !== 'granted';
        nd.style.display = (unread || needsPermission) ? 'block' : 'none';
    }

    function _renderPanel() {
        const list = document.getElementById('notifList');
        if (!list) return;
        const items = _loadNotifications();
        if (!items.length) {
            list.innerHTML = '<div class="notif-empty">Aucune notification pour le moment</div>';
            return;
        }
        list.innerHTML = items.map(function(n, i) {
            return '<div class="notif-item' + (n.read ? '' : ' unread') + '" onclick="FCM.openNotification(' + i + ')">'
                + '<div class="notif-item-title">' + _esc(n.title) + '</div>'
                + '<div class="notif-item-body">' + _esc(n.body) + '</div>'
                + '<div class="notif-item-time">' + _esc(n.time || '') + '</div>'
                + '</div>';
        }).join('');
    }

    function _esc(s) {
        return String(s || '').replace(/&/g, '&amp;').replace(/</g, '&lt;').replace(/>/g, '&gt;');
    }

    function _updateNotifButton() {
        const btn = document.getElementById('notifEnableBtn');
        if (!btn) return;
        if (Notification.permission === 'granted') {
            btn.textContent = 'Notifications activées';
            btn.disabled = true;
        } else if (Notification.permission === 'denied') {
            btn.textContent = 'Notifications bloquées';
            btn.title = 'Réinitialisez l\'autorisation via l\'icône à gauche de l\'URL du site';
        } else {
            btn.textContent = 'Activer les notifications';
            btn.disabled = false;
            btn.title = '';
        }
    }

    function _permissionBlockedMessage() {
        return 'Les notifications sont bloquées par votre navigateur. '
            + 'Cliquez sur l\'icône à gauche de l\'adresse du site (cadenas ou réglages), '
            + 'ouvrez « Autorisations » / « Paramètres du site », puis autorisez les notifications.';
    }

    function _addNotification(title, body, data) {
        const items = _loadNotifications();
        items.unshift({
            title: title || 'Notification',
            body:  body || '',
            data:  data || {},
            time:  new Date().toLocaleString('fr-FR'),
            read:  false,
        });
        _saveNotifications(items);
        _updateDot();
        _renderPanel();
    }

    async function _syncTokenToSW(token) {
        if (!token) return;
        try {
            if ('caches' in window) {
                const cache = await caches.open('sinistre-config');
                await cache.put('/sw-fcm-token', new Response(token, {
                    headers: { 'Content-Type': 'text/plain' },
                }));
            }
        } catch (e) {
            console.warn('[FCM] token cache sync failed', e);
        }
        if (navigator.serviceWorker?.controller) {
            navigator.serviceWorker.controller.postMessage({ type: 'FCM_TOKEN', token });
        }
    }

    async function _showNewMissionNotification(title, body, data) {
        if (!('Notification' in window) || Notification.permission !== 'granted') return;
        try {
            const reg = await navigator.serviceWorker.ready;
            await reg.showNotification(title || 'Sinistre Pro', {
                body: body || 'Nouvelle mission disponible',
                icon: '/sinistre_services/static/pwa/icons/icon-192.png',
                badge: '/sinistre_services/static/pwa/icons/badge-72.png',
                tag: data.mission_id ? `mission-${data.mission_id}` : 'sinistre-notif',
                renotify: true,
                requireInteraction: true,
                data,
                actions: [
                    { action: 'accepter', title: '✅ Accepter' },
                    { action: 'refuser', title: '❌ Refuser' },
                ],
            });
        } catch (e) {
            console.warn('[FCM] showNotification failed', e);
        }
    }

    return {
        init() {
            if (_initialized) return;
            try {
                if (!firebase.apps.length) {
                    firebase.initializeApp(CONFIG.FIREBASE);
                }
                _messaging = firebase.messaging();
                _initialized = true;
                this._onForegroundMessage();
                _updateDot();
                _renderPanel();
                _updateNotifButton();
            } catch (err) {
                console.warn('[FCM] Init error:', err);
            }
        },

        togglePanel() {
            const panel = document.getElementById('notifPanel');
            if (!panel) return;
            _panelOpen = !_panelOpen;
            panel.style.display = _panelOpen ? 'block' : 'none';
            if (_panelOpen) {
                _renderPanel();
                _updateNotifButton();
            }
        },

        closePanel() {
            const panel = document.getElementById('notifPanel');
            if (panel) panel.style.display = 'none';
            _panelOpen = false;
        },

        openNotification(index) {
            const items = _loadNotifications();
            const n = items[index];
            if (!n) return;
            n.read = true;
            _saveNotifications(items);
            _updateDot();
            _renderPanel();
            this.closePanel();
            if (n.data && n.data.mission_id && window.MissionDetail) {
                MissionDetail.open(n.data.mission_id);
            } else if (window.App && App.currentView !== 'dashboard') {
                App.showView('dashboard', document.getElementById('nav-dashboard'));
            }
        },

        clearAll() {
            _saveNotifications([]);
            _updateDot();
            _renderPanel();
        },

        async requestPermission() {
            if (!_messaging) { this.init(); }

            if (Notification.permission === 'denied') {
                Toast.show(_permissionBlockedMessage(), 'warning', 9000);
                _updateNotifButton();
                _updateDot();
                return;
            }

            if (Notification.permission === 'granted') {
                _updateNotifButton();
                try {
                    _token = await _messaging.getToken({ vapidKey: CONFIG.FIREBASE_VAPID_KEY });
                    if (_token) {
                        await API.saveFCMToken(_token);
                        localStorage.setItem('ss_fcm_token', _token);
                        await _syncTokenToSW(_token);
                        Toast.show('🔔 Notifications déjà activées', 'success');
                    }
                } catch (err) {
                    console.error('[FCM] getToken error:', err);
                    Toast.show('Erreur activation notifications', 'error');
                }
                return;
            }

            let permission;
            try {
                permission = await Notification.requestPermission();
            } catch (err) {
                console.warn('[FCM] requestPermission error:', err);
                if (Notification.permission === 'denied') {
                    Toast.show(_permissionBlockedMessage(), 'warning', 9000);
                } else {
                    Toast.show('Impossible d\'afficher la demande de notification', 'error');
                }
                _updateNotifButton();
                _updateDot();
                return;
            }

            if (permission !== 'granted') {
                const msg = permission === 'denied'
                    ? _permissionBlockedMessage()
                    : 'Notifications refusées';
                Toast.show(msg, 'warning', permission === 'denied' ? 9000 : 5000);
                _updateNotifButton();
                _updateDot();
                return;
            }

            try {
                _token = await _messaging.getToken({ vapidKey: CONFIG.FIREBASE_VAPID_KEY });
                if (_token) {
                    await API.saveFCMToken(_token);
                    localStorage.setItem('ss_fcm_token', _token);
                    await _syncTokenToSW(_token);
                    _updateDot();
                    _updateNotifButton();
                    Toast.show('🔔 Notifications activées', 'success');
                }
            } catch (err) {
                console.error('[FCM] getToken error:', err);
                Toast.show('Erreur activation notifications', 'error');
            }
        },

        _onForegroundMessage() {
            if (!_messaging) return;
            _messaging.onMessage(async (payload) => {
                console.log('[FCM] Foreground message:', payload);
                const data = payload.data || {};
                const title = payload.notification?.title || data.title;
                const body = payload.notification?.body || data.body;

                if (data.type === 'new_mission' && data.mission_id) {
                    await _showNewMissionNotification(title, body, data);
                } else {
                    Toast.show(`🔔 ${title}: ${body}`, 'info', 6000);
                }
                if (navigator.vibrate) navigator.vibrate([200, 100, 200]);

                _addNotification(title, body, data);

                if (window.App && App.currentView === 'dashboard' && window.Dashboard) {
                    Dashboard.refresh();
                }
            });
        },

        async autoInit() {
            this.init();
            if (Notification.permission === 'granted' && _messaging) {
                try {
                    _token = await _messaging.getToken({ vapidKey: CONFIG.FIREBASE_VAPID_KEY });
                    if (_token) {
                        await API.saveFCMToken(_token);
                        await _syncTokenToSW(_token);
                    }
                } catch (err) {
                    console.warn('[FCM] autoInit token error:', err);
                }
            }
            _updateDot();
            _updateNotifButton();
        },

        getToken() { return _token; },
    };
})();

document.addEventListener('click', function(e) {
    const wrap = document.querySelector('.notif-wrap');
    if (!wrap || wrap.contains(e.target)) return;
    if (window.FCM) FCM.closePanel();
});
