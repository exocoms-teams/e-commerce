/**
 * offline.js — File d'attente pour les actions hors ligne
 * Stocke en IndexedDB, rejoue automatiquement quand le réseau revient
 */

window.Offline = (() => {
    const DB_NAME    = 'sinistre-offline';
    const DB_VERSION = 1;
    const STORE      = 'queue';
    let _db = null;
    let _isOnline = navigator.onLine;

    /* ── IndexedDB ── */
    function openDB() {
        return new Promise((resolve, reject) => {
            if (_db) { resolve(_db); return; }
            const req = indexedDB.open(DB_NAME, DB_VERSION);
            req.onupgradeneeded = (e) => {
                const db = e.target.result;
                if (!db.objectStoreNames.contains(STORE)) {
                    db.createObjectStore(STORE, { keyPath: 'id', autoIncrement: true });
                }
            };
            req.onsuccess = (e) => { _db = e.target.result; resolve(_db); };
            req.onerror   = () => reject(req.error);
        });
    }

    async function addToQueue(action) {
        const db    = await openDB();
        const store = db.transaction(STORE, 'readwrite').objectStore(STORE);
        store.add({ ...action, timestamp: Date.now(), retries: 0 });
    }

    async function getQueue() {
        const db    = await openDB();
        return new Promise((resolve) => {
            const store = db.transaction(STORE, 'readonly').objectStore(STORE);
            const req   = store.getAll();
            req.onsuccess = () => resolve(req.result || []);
            req.onerror   = () => resolve([]);
        });
    }

    async function removeFromQueue(id) {
        const db    = await openDB();
        const store = db.transaction(STORE, 'readwrite').objectStore(STORE);
        store.delete(id);
    }

    async function clearQueue() {
        const db    = await openDB();
        const store = db.transaction(STORE, 'readwrite').objectStore(STORE);
        store.clear();
    }

    /* ── Rejouer la queue ── */
    async function processQueue() {
        if (!_isOnline) return;
        const queue = await getQueue();
        if (!queue.length) return;

        console.log(`[Offline] Rejoue ${queue.length} action(s)`);
        Toast.show(`📡 Synchronisation de ${queue.length} action(s)…`);

        let success = 0, errors = 0;

        for (const item of queue) {
            try {
                await executeAction(item);
                await removeFromQueue(item.id);
                success++;
            } catch (err) {
                console.error(`[Offline] Erreur action ${item.type}:`, err);
                errors++;
                if (item.retries >= 3) {
                    await removeFromQueue(item.id); // abandon après 3 essais
                }
            }
        }

        if (success > 0) Toast.show(`✅ ${success} action(s) synchronisée(s)`, 'success');
        if (errors > 0)  Toast.show(`⚠️ ${errors} action(s) en échec`, 'warning');

        // Rafraîchir le dashboard
        if (App.currentView === 'dashboard') Dashboard.refresh();
    }

    /* ── Exécuter une action de la queue ── */
    async function executeAction(item) {
        switch (item.type) {
            case 'UPLOAD_PHOTO':
                return API.uploadPhoto(item.missionId, item.photoType, item.base64, item.description);
            case 'CREATE_DEVIS':
                return API.createDevis(item.missionId, item.payload);
            case 'ENVOYER_DEVIS':
                return API.envoyerDevis(item.devisId);
            case 'ACCEPTER_DEVIS':
                return API.accepterDevis(item.devisId, item.signature);
            case 'REFUSER_DEVIS':
                return API.refuserDevis(item.devisId);
            case 'DEMARRER_MISSION':
                return API.demarrer(item.missionId);
            case 'TERMINER_MISSION':
                return API.terminer(item.missionId);
            default:
                console.warn('[Offline] Action inconnue:', item.type);
        }
    }

    /* ── Surveiller le réseau ── */
    window.addEventListener('online', () => {
        _isOnline = true;
        document.querySelector('.offline-banner')?.remove();
        Toast.show('🌐 Connexion rétablie', 'success');
        processQueue();
    });

    window.addEventListener('offline', () => {
        _isOnline = false;
        if (!document.querySelector('.offline-banner')) {
            const banner = document.createElement('div');
            banner.className = 'offline-banner';
            banner.textContent = '📡 Mode hors ligne — vos actions seront envoyées à la reconnexion';
            document.body.appendChild(banner);
        }
    });

    /* ── Écouter le SW (background sync) ── */
    navigator.serviceWorker?.addEventListener('message', (event) => {
        if (event.data?.type === 'PROCESS_OFFLINE_QUEUE') {
            processQueue();
        }
        if (event.data?.type === 'OPEN_MISSION') {
            MissionDetail.open(event.data.missionId);
        }
    });

    /* ── API publique ── */
    return {
        isOnline: () => _isOnline,

        async enqueue(type, payload) {
            await addToQueue({ type, ...payload });
            Toast.show('📡 Action enregistrée — sera envoyée à la reconnexion', 'warning');
        },

        processQueue,
        getQueue,
        clearQueue,

        /* ── Wrapper : essaie en ligne, sinon met en queue ── */
        async tryOrQueue(type, apiFn, queuePayload) {
            if (_isOnline) {
                return apiFn();
            } else {
                await this.enqueue(type, queuePayload);
                return { queued: true };
            }
        },
    };
})();
