/**
 * api.js — Client HTTP vers l'API Odoo
 * Gère : authentification session, erreurs, offline queue
 */

window.API = (() => {
    const BASE = CONFIG.ODOO_BASE_URL + CONFIG.API_BASE;

    /* ── Headers de base ── */
    function headers(extra = {}) {
        return {
            'Content-Type': 'application/json',
            'Accept': 'application/json',
            ...extra,
        };
    }

    /* ── Requête générique ── */
    async function request(method, path, body = null, options = {}) {
        const url = path.startsWith('http') ? path : BASE + path;
        const opts = {
            method,
            credentials: 'include',          // session cookie Odoo
            headers: headers(options.headers || {}),
        };
        if (body) opts.body = JSON.stringify(body);

        try {
            const response = await fetch(url, opts);

            // Redirigé vers login → session expirée
            if (response.redirected && response.url.includes('/web/login')) {
                Auth.logout();
                throw new Error('Session expirée');
            }

            const data = await response.json();

            if (!response.ok) {
                throw new Error(data.error || `HTTP ${response.status}`);
            }
            return data;
        } catch (err) {
            if (err.message === 'Failed to fetch' || err.message.includes('NetworkError')) {
                throw new Error('OFFLINE');
            }
            throw err;
        }
    }

    /* ── Méthodes publiques ── */
    return {
        get:    (path, opts) => request('GET', path, null, opts),
        post:   (path, body, opts) => request('POST', path, body, opts),
        put:    (path, body, opts) => request('PUT', path, body, opts),
        patch:  (path, body, opts) => request('PATCH', path, body, opts),

        /* ── Me (session + intervenant info) ── */
        async getMe() {
            return this.get('/me');
        },

        /* ── Missions ── */
        async getMissions() {
            return this.get('/intervenant/missions');
        },

        async getMission(id) {
            return this.get(`/mission/${id}`);
        },

        /* ── Actions sur mission ── */
        async demarrer(missionId) {
            return this.post(`/intervenant/mission/${missionId}/demarrer`, {});
        },

        async terminer(missionId) {
            return this.post(`/intervenant/mission/${missionId}/terminer`, {});
        },

        /* ── Devis ── */
        async createDevis(missionId, payload) {
            return this.post(`/intervenant/mission/${missionId}/devis`, payload);
        },

        async envoyerDevis(devisId) {
            return this.post(`/intervenant/devis/${devisId}/envoyer`, {});
        },

        async accepterDevis(devisId, signatureBase64) {
            return this.post(`/intervenant/devis/${devisId}/accepter`, {
                signature: signatureBase64,
            });
        },

        async refuserDevis(devisId) {
            return this.post(`/intervenant/devis/${devisId}/refuser`, {});
        },

        /* ── Photos ── */
        async uploadPhoto(missionId, type, base64Data, description = '') {
            return this.post(`/intervenant/mission/${missionId}/photo`, {
                type_photo: type,   // 'avant' | 'apres'
                image: base64Data,  // base64 sans data:url prefix
                description,
            });
        },

        /* ── FCM Token ── */
        async saveFCMToken(token) {
            return this.post('/intervenant/fcm-token', { token });
        },

        /* ── Auth Odoo (via JSON-RPC standard) ── */
        async login(email, password) {
            const url = CONFIG.ODOO_BASE_URL + '/web/session/authenticate';
            const response = await fetch(url, {
                method: 'POST',
                credentials: 'include',
                headers: { 'Content-Type': 'application/json' },
                body: JSON.stringify({
                    jsonrpc: '2.0',
                    method: 'call',
                    params: {
                        db: window.location.hostname.split('.')[0] || 'sinistre',   // auto-détecté
                        login: email,
                        password: password,
                    },
                }),
            });
            const data = await response.json();
            if (data.result && data.result.uid) {
                return { success: true, user: data.result };
            }
            throw new Error(data.error?.data?.message || 'Identifiants incorrects');
        },

        async logout() {
            await fetch(CONFIG.ODOO_BASE_URL + '/web/session/destroy', {
                method: 'POST',
                credentials: 'include',
                headers: { 'Content-Type': 'application/json' },
                body: JSON.stringify({ jsonrpc: '2.0', method: 'call', params: {} }),
            });
        },

        async getSession() {
            const response = await fetch(CONFIG.ODOO_BASE_URL + '/web/session/get_session_info', {
                method: 'POST',
                credentials: 'include',
                headers: { 'Content-Type': 'application/json' },
                body: JSON.stringify({ jsonrpc: '2.0', method: 'call', params: {} }),
            });
            const data = await response.json();
            return data.result;
        },
    };
})();
