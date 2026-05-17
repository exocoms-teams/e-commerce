/**
 * Service Worker — Sinistre Pro PWA
 * Stratégies de cache + gestion des notifications push Firebase
 */

importScripts('https://www.gstatic.com/firebasejs/10.12.0/firebase-app-compat.js');
importScripts('https://www.gstatic.com/firebasejs/10.12.0/firebase-messaging-compat.js');

const CACHE_NAME = 'sinistre-pro-v3';
const OFFLINE_URL = '/pwa/offline.html';

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

// Notification push reçue en background (app fermée / onglet inactif)
messaging.onBackgroundMessage((payload) => {
    console.log('[SW] Push reçu en background', payload);

    const { title, body, icon, data = {} } = payload.notification || {};

    self.registration.showNotification(title || 'Sinistre Pro', {
        body: body || 'Nouvelle mission disponible',
        icon: icon || '/pwa/icons/icon-192.png',
        badge: '/pwa/icons/badge-72.png',
        tag: data.mission_id ? `mission-${data.mission_id}` : 'sinistre-notif',
        renotify: true,
        requireInteraction: true,          // reste affichée jusqu'au clic
        vibrate: [200, 100, 200, 100, 400],
        actions: [
            { action: 'voir', title: '👁 Voir la mission' },
            { action: 'ignorer', title: 'Plus tard' }
        ],
        data: data,
    });
});

// ─── CLICK sur notification ────────────────────────────────────────
self.addEventListener('notificationclick', (event) => {
    event.notification.close();

    const { action, notification } = event;
    const data = notification.data || {};

    if (action === 'ignorer') return;

    const targetUrl = data.mission_id
        ? `/pwa/?mission=${data.mission_id}`
        : '/pwa/';

    event.waitUntil(
        clients.matchAll({ type: 'window', includeUncontrolled: true }).then((windowClients) => {
            // Activer une fenêtre déjà ouverte
            for (const client of windowClients) {
                if (client.url.includes('/pwa/') && 'focus' in client) {
                    client.postMessage({ type: 'OPEN_MISSION', missionId: data.mission_id });
                    return client.focus();
                }
            }
            // Sinon ouvrir une nouvelle fenêtre
            return clients.openWindow(targetUrl);
        })
    );
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
