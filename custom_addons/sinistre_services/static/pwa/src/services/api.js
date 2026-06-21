/**
 * api.js — Client HTTP vers l'API Odoo
 * Gère : authentification session, erreurs, offline queue
 *
 * Nouveaux endpoints :
 *  - signerAvant / signerApres           (signatures intervention)
 *  - updateDevis                          (modification devis + avenant)
 *  - accepterDevis (avec flag isModified) (re-signature)
 *  - getMessages / sendMessage / marquerLu (messagerie)
 *  - saveNotes                            (notes artisan)
 */

window.API = (() => {
    const BASE = CONFIG.ODOO_BASE_URL + CONFIG.API_BASE;

    function headers(extra = {}) {
        return { 'Content-Type': 'application/json', 'Accept': 'application/json', ...extra };
    }

    async function request(method, path, body = null, options = {}) {
        const url  = path.startsWith('http') ? path : BASE + path;
        const opts = {
            method,
            credentials: 'include',
            headers: headers(options.headers || {}),
        };
        if (body) opts.body = JSON.stringify(body);
        try {
            const response = await fetch(url, opts);
            if (response.redirected && response.url.includes('/web/login')) {
                Auth.logout();
                throw new Error('Session expirée');
            }
            const data = await response.json();
            if (!response.ok) throw new Error(data.error || `HTTP ${response.status}`);
            return data;
        } catch (err) {
            if (err.message === 'Failed to fetch' || err.message.includes('NetworkError')) {
                throw new Error('OFFLINE');
            }
            throw err;
        }
    }

    return {
        get:   (path, opts) => request('GET',   path, null, opts),
        post:  (path, body, opts) => request('POST',  path, body, opts),
        put:   (path, body, opts) => request('PUT',   path, body, opts),
        patch: (path, body, opts) => request('PATCH', path, body, opts),

        /* ── Session ── */
        async getMe()      { return this.get('/me'); },

        /* ── Missions ── */
        async getMissions()  { return this.get('/intervenant/missions'); },
        async getMission(id) { return this.get(`/mission/${id}`); },

        /* ── Workflow mission ── */
        async demarrer(missionId)  { return this.post(`/intervenant/mission/${missionId}/demarrer`, {}); },
        async terminer(missionId)  { return this.post(`/intervenant/mission/${missionId}/terminer`, {}); },

        /* ── Signatures avant / après ── */
        async signerAvant(missionId, signatureBase64) {
            return this.post(`/intervenant/mission/${missionId}/signature-avant`, {
                signature: signatureBase64,
            });
        },
        async signerApres(missionId, signatureBase64) {
            return this.post(`/intervenant/mission/${missionId}/signature-apres`, {
                signature: signatureBase64,
            });
        },

        /* ── Devis ── */
        async createDevis(missionId, payload) {
            return this.post(`/intervenant/mission/${missionId}/devis`, payload);
        },
        async updateDevis(devisId, payload) {
            return this.put(`/intervenant/devis/${devisId}`, payload);
        },
        async envoyerDevis(devisId) {
            return this.post(`/intervenant/devis/${devisId}/envoyer`, {});
        },
        async accepterDevis(devisId, signatureBase64, isModified = false) {
            return this.post(`/intervenant/devis/${devisId}/accepter`, {
                signature:   signatureBase64,
                is_modified: isModified,
            });
        },
        async refuserDevis(devisId) {
            return this.post(`/intervenant/devis/${devisId}/refuser`, {});
        },

        /* ── Photos ── */
        async uploadPhoto(missionId, type, base64Data, description = '') {
            return this.post(`/intervenant/mission/${missionId}/photo`, {
                type_photo:  type,
                image:       base64Data,
                description: description || '',
            });
        },

        /* ── Notes artisan ── */
        async saveNotes(missionId, texte) {
            return this.post(`/intervenant/mission/${missionId}/notes`, { notes: texte });
        },

        /* ── Messagerie ── */
        async getMessages(missionId) {
            return this.get(`/intervenant/mission/${missionId}/messages`);
        },
        async sendMessage(missionId, contenu) {
            return this.post(`/intervenant/mission/${missionId}/messages`, { contenu });
        },
        async marquerLu(missionId) {
            return this.post(`/intervenant/mission/${missionId}/messages/lus`, {});
        },

        /* ── FCM Token ── */
        async getMissionsProposees() {
            return this.get('/intervenant/missions/proposees');
        },
        async accepterMissionProposee(missionId) {
            return this.post(`/intervenant/mission/${missionId}/accepter`, {});
        },
        async refuserMissionProposee(missionId) {
            return this.post(`/intervenant/mission/${missionId}/refuser-proposition`, {});
        },

        async saveFCMToken(token) {
            return this.post('/intervenant/fcm-token', { token });
        },

        /* ── Comptabilité ── */
        async getComptabilite() {
            return this.get('/intervenant/comptabilite');
        },

        async getFacturesAFournir() {
            return this.get('/intervenant/factures-a-fournir');
        },

        /* ── Auth Odoo ── */
        async login(email, password) {
            const url  = CONFIG.ODOO_BASE_URL + '/web/session/authenticate';
            const resp = await fetch(url, {
                method: 'POST', credentials: 'include',
                headers: { 'Content-Type': 'application/json' },
                body: JSON.stringify({
                    jsonrpc: '2.0', method: 'call',
                    params: {
                        db: window.location.hostname.split('.')[0] || 'sinistre',
                        login: email, password,
                    },
                }),
            });
            const data = await resp.json();
            if (data.result?.uid) return { success: true, user: data.result };
            throw new Error(data.error?.data?.message || 'Identifiants incorrects');
        },
        async logout() {
            await fetch(CONFIG.ODOO_BASE_URL + '/web/session/destroy', {
                method: 'POST', credentials: 'include',
                headers: { 'Content-Type': 'application/json' },
                body: JSON.stringify({ jsonrpc: '2.0', method: 'call', params: {} }),
            });
        },
        async getSession() {
            const resp = await fetch(CONFIG.ODOO_BASE_URL + '/web/session/get_session_info', {
                method: 'POST', credentials: 'include',
                headers: { 'Content-Type': 'application/json' },
                body: JSON.stringify({ jsonrpc: '2.0', method: 'call', params: {} }),
            });
            return (await resp.json()).result;
        },
    };
})();
