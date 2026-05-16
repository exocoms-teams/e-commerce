/**
 * fcm.js — Firebase Cloud Messaging
 * Initialise Firebase, gère la permission, reçoit les push en foreground
 */

window.FCM = (() => {
    let _messaging = null;
    let _token = null;
    let _initialized = false;

    return {
        /* ── Initialisation ── */
        init() {
            if (_initialized) return;
            try {
                if (!firebase.apps.length) {
                    firebase.initializeApp(CONFIG.FIREBASE);
                }
                _messaging = firebase.messaging();
                _initialized = true;
                this._onForegroundMessage();
            } catch (err) {
                console.warn('[FCM] Init error:', err);
            }
        },

        /* ── Demander la permission push ── */
        async requestPermission() {
            if (!_messaging) { this.init(); }

            const permission = await Notification.requestPermission();
            if (permission !== 'granted') {
                Toast.show('Notifications refusées', 'warning');
                return;
            }

            try {
                _token = await _messaging.getToken({ vapidKey: CONFIG.FIREBASE_VAPID_KEY });
                if (_token) {
                    await API.saveFCMToken(_token);
                    localStorage.setItem('ss_fcm_token', _token);
                    document.getElementById('notifDot').style.display = 'none';
                    Toast.show('🔔 Notifications activées', 'success');
                }
            } catch (err) {
                console.error('[FCM] getToken error:', err);
                Toast.show('Erreur activation notifications', 'error');
            }
        },

        /* ── Notif reçue quand l'app est au premier plan ── */
        _onForegroundMessage() {
            if (!_messaging) return;
            _messaging.onMessage((payload) => {
                console.log('[FCM] Foreground message:', payload);
                const { title, body } = payload.notification || {};
                const data = payload.data || {};

                // Toast visible + vibration
                Toast.show(`🔔 ${title}: ${body}`, 'info', 6000);
                if (navigator.vibrate) navigator.vibrate([200, 100, 200]);

                // Rafraîchir la liste si on est sur le dashboard
                if (App.currentView === 'dashboard') {
                    Dashboard.refresh();
                }

                // Marquer qu'il y a une nouvelle notif
                document.getElementById('notifDot').style.display = 'block';
            });
        },

        /* ── Auto-init si token déjà accordé ── */
        async autoInit() {
            this.init();
            if (Notification.permission === 'granted' && _messaging) {
                try {
                    _token = await _messaging.getToken({ vapidKey: CONFIG.FIREBASE_VAPID_KEY });
                    if (_token) {
                        await API.saveFCMToken(_token);
                    }
                } catch (err) {
                    console.warn('[FCM] autoInit token error:', err);
                }
            } else if (Notification.permission === 'default') {
                // Montrer le bouton notification
                document.getElementById('notifDot').style.display = 'block';
            }
        },

        getToken() { return _token; },
    };
})();
