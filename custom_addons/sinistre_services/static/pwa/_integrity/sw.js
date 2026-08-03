/**
 * Service Worker — Sinistre Pro PWA
 * Stratégies de cache + gestion des notifications push Firebase
 */

importScripts('https://www.gstatic.com/firebasejs/10.12.0/firebase-app-compat.js');
importScripts('https://www.gstatic.com/firebasejs/10.12.0/firebase-messaging-compat.js');

const CACHE_NAME = 'sinistre-pro-v6';
const OFFLINE_URL = '/pwa/offline.html';
const API_BASE = '/api/sinistre/v1';
const PWA_ICON = '/sinistre_services/static/pwa/icons/icon-192.png';
const PWA_BADGE = '/sinistre_services/static/pwa/icons/badge-72.png';
const FCM_TOKEN_CACHE = 'sinistre-config';
const FCM_TOKEN_KEY = '/sw-fcm-token';

let _cachedFcmToken = null;

// ─── Ressources à précacher ───────────────────────────────────────
const PRECACHE_URLS = [
    '/pwa/',
    '/pwa/index.html',
    '/pwa/offline.html',
    '/pwa/manifest.json',
    '/pwa/src/styles/main.css',
    '/pwa/src/services/config.js',
    '/pwa/src/services/api.js',
    '/pwa/src/services/auth.js',
    '/pwa/src/services/fcm.js',
    '/pwa/src/services/offline.js',
    '/pwa/src/components/toast.js',
    '/pwa/src/components/photos.js',
    '/pwa/src/components/signature.js',
    '/pwa/src/components/devis.js',
    '/pwa/src/screens/dashboard.js',
    '/pwa/src/screens/mission_detail.js',
    '/pwa/src/app.js',
    'https://fonts.googleapis.com/css2?family=Poppins:wght@400;500;600;700&family=Roboto:wght@300;400;500&display=swap',
];

// ─── INSTALL ──────────────────────────────────────────────────────
self.addEventListener('install', (event) => {
    event.waitUntil(
        caches.open(CACHE_NAME).then((cache) => {
            return cache.addAll(PRECACHE_URLS.map(url => new Request(url, { mode: 'no-cors' })));
        }).then(() => self.skipWaiting())
    );
});

// ─── ACTIVATE ─────────────────────────────────────────────────────
self.addEventListener('activate', (event) => {
    event.waitUntil(
        caches.keys().then((keys) =>
            Promise.all(
                keys.filter(key => key !== CACHE_NAME)
                    .map(key => caches.delete(key))
            )
        ).then(() => self.clients.claim())
    );
});

// ─── FETCH — Stratégie Network-First pour l'API, Cache-First pour assets ──
self.addEventListener('fetch', (event) => {
    const { request } = event;
    const url = new URL(request.url);

    // API Odoo → network first, fallback queue offline
    if (url.pathname.startsWith('/api/sinistre/')) {
        event.respondWith(networkFirst(request));
        return;
    }

    // Assets statiques → cache first
    if (request.destination === 'image' ||
        request.destination === 'style' ||
        request.destination === 'script') {
        event.respondWith(cacheFirst(request));
        return;
    }

    // Navigation → network first, fallback offline.html
    if (request.mode === 'navigate') {
        event.respondWith(
            fetch(request).catch(() => caches.match(OFFLINE_URL))
        );
        return;
    }

    event.respondWith(networkFirst(request));
});

async function cacheFirst(request) {
    const cached = await caches.match(request);
    if (cached) return cached;
    try {
        const response = await fetch(request);
        if (response.ok) {
            const cache = await caches.open(CACHE_NAME);
            cache.put(request, response.clone());
        }
        return response;
    } catch {
        return cached || new Response('Offline', { status: 503 });
    }
}

async function networkFirst(request) {
    try {
        const response = await fetch(request);
        if (response.ok && request.method === 'GET') {
            const cache = await caches.open(CACHE_NAME);
            cache.put(request, response.clone());
        }
        return response;
    } catch {
        const cached = await caches.match(request);
        return cached || new Response(
            JSON.stringify({ error: 'Vous êtes hors ligne', offline: true }),
            { status: 503, headers: { 'Content-Type': 'application/json' } }
        );
    }
}

// ─── FIREBASE MESSAGING (background push) ─────────────────────────
firebase.initializeApp({
    apiKey: '__FIREBASE_API_KEY__',
    authDomain: '__FIREBASE_AUTH_DOMAIN__',
    projectId: '__FIREBASE_PROJECT_ID__',
    storageBucket: '__FIREBASE_STORAGE_BUCKET__',
    messagingSenderId: '__FIREBASE_SENDER_ID__',
    appId: '__FIREBASE_APP_ID__'
});

const messaging = firebase.messaging();

function _isNewMissionData(data) {
    return data && data.type === 'new_mission' && data.mission_id;
}

async function getFcmToken() {
    if (_cachedFcmToken) return _cachedFcmToken;
    try {
        const cache = await caches.open(FCM_TOKEN_CACHE);
        const resp = await cache.match(FCM_TOKEN_KEY);
        if (resp) {
            _cachedFcmToken = (await resp.text()).trim();
        }
    } catch (e) {
        console.warn('[SW] FCM token cache read failed', e);
    }
    return _cachedFcmToken;
}

function showMissionNotification(payload) {
    const notif = payload.notification || {};
    const data = { ...(payload.data || notif.data || {}) };
    const title = notif.title || data.title;
    const body = notif.body || data.body;
    const icon = notif.icon || data.icon;
    const missionId = data.mission_id;
    const isNewMission = _isNewMissionData(data);

    const options = {
        body: body || 'Nouvelle mission disponible',
        icon: icon || PWA_ICON,
        badge: PWA_BADGE,
        tag: missionId ? `mission-${missionId}` : 'sinistre-notif',
        renotify: true,
        requireInteraction: isNewMission,
        vibrate: [200, 100, 200, 100, 400],
        data,
    };

    if (isNewMission) {
        options.actions = [
            { action: 'accepter', title: '✅ Accepter' },
            { action: 'refuser', title: '❌ Refuser' },
        ];
    } else {
        options.actions = [
            { action: 'voir', title: '👁 Voir' },
        ];
    }

    return self.registration.showNotification(title || 'Sinistre Pro', options);
}

async function missionReponsePush(missionId, reponse) {
    const fcmToken = await getFcmToken();
    if (!fcmToken) {
        return { ok: false, error: 'Token FCM introuvable — ouvrez l\'app et activez les notifications' };
    }

    const response = await fetch(
        `${API_BASE}/intervenant/mission/${missionId}/reponse-push`,
        {
            method: 'POST',
            credentials: 'include',
            headers: {
                'Content-Type': 'application/json',
                'Accept': 'application/json',
            },
            body: JSON.stringify({ fcm_token: fcmToken, reponse }),
        }
    );

    let data = {};
    try { data = await response.json(); } catch (e) { /* ignore */ }

    if (!response.ok) {
        return { ok: false, error: data.error || `Erreur HTTP ${response.status}` };
    }
    return { ok: true, data, reponse };
}

async function notifyClients(message) {
    const allClients = await clients.matchAll({ type: 'window', includeUncontrolled: true });
    allClients.forEach((client) => client.postMessage(message));
}

async function showActionResult(title, body, tag) {
    await self.registration.showNotification(title, {
        body,
        tag: tag || 'sinistre-action-result',
        renotify: true,
        icon: PWA_ICON,
    });
}

async function openMissionInApp(missionId) {
    const targetUrl = missionId ? `/pwa/?mission=${missionId}` : '/pwa/';
    const windowClients = await clients.matchAll({ type: 'window', includeUncontrolled: true });
    for (const client of windowClients) {
        if (client.url.includes('/pwa/') && 'focus' in client) {
            client.postMessage({ type: 'OPEN_MISSION', missionId });
            return client.focus();
        }
    }
    return clients.openWindow(targetUrl);
}

// Notification push reçue en background (app fermée / onglet inactif)
messaging.onBackgroundMessage((payload) => {
    console.log('[SW] Push reçu en background', payload);
    return showMissionNotification(payload);
});

// ─── CLICK sur notification ────────────────────────────────────────
self.addEventListener('notificationclick', (event) => {
    event.notification.close();

    const { action } = event;
    const data = event.notification.data || {};
    const missionId = data.mission_id;

    if (action === 'accepter' && missionId) {
        event.waitUntil((async () => {
            const result = await missionReponsePush(missionId, 'accepte');
            if (result.ok) {
                await showActionResult(
                    '✅ Mission acceptée',
                    'La mission est disponible dans Mes Missions.',
                    `mission-accepted-${missionId}`
                );
                await notifyClients({ type: 'MISSION_ACCEPTED', missionId, data: result.data });
                await openMissionInApp(missionId);
            } else {
                await showActionResult('⚠️ Acceptation impossible', result.error, 'mission-action-error');
                await notifyClients({ type: 'MISSION_ACTION_ERROR', message: result.error, missionId });
            }
        })());
        return;
    }

    if (action === 'refuser' && missionId) {
        event.waitUntil((async () => {
            const result = await missionReponsePush(missionId, 'refuse');
            if (result.ok) {
                await showActionResult('Mission refusée', 'Proposition ignorée.', `mission-refused-${missionId}`);
                await notifyClients({ type: 'MISSION_REFUSED', missionId });
            } else {
                await showActionResult('⚠️ Refus impossible', result.error, 'mission-action-error');
                await notifyClients({ type: 'MISSION_ACTION_ERROR', message: result.error, missionId });
            }
        })());
        return;
    }

    if (action === 'ignorer') return;

    event.waitUntil(openMissionInApp(missionId));
});

// ─── Messages depuis l'app (token FCM, sync offline) ───────────────
self.addEventListener('message', (event) => {
    const msg = event.data || {};
    if (msg.type === 'FCM_TOKEN' && msg.token) {
        _cachedFcmToken = String(msg.token).trim();
        event.waitUntil((async () => {
            try {
                const cache = await caches.open(FCM_TOKEN_CACHE);
                await cache.put(FCM_TOKEN_KEY, new Response(_cachedFcmToken, {
                    headers: { 'Content-Type': 'text/plain' },
                }));
            } catch (e) {
                console.warn('[SW] FCM token cache write failed', e);
            }
        })());
    }
});

// ─── SYNC background (envoi offline queue) ────────────────────────
self.addEventListener('sync', (event) => {
    if (event.tag === 'sync-offline-queue') {
        event.waitUntil(syncOfflineQueue());
    }
});

async function syncOfflineQueue() {
    // Signaler à l'app de traiter la queue
    const allClients = await clients.matchAll({ type: 'window' });
    allClients.forEach(client => {
        client.postMessage({ type: 'PROCESS_OFFLINE_QUEUE' });
    });
}
