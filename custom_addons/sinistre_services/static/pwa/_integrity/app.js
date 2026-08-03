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
        let existing = {};
        try { existing = JSON.parse(localStorage.getItem('ss_user') || '{}'); } catch(e) {}
        try {
            const resp = await fetch('/api/sinistre/v1/me', { credentials: 'include' });
            if (!resp.ok) {
                let errMsg = '';
                try {
                    const errBody = await resp.json();
                    errMsg = errBody.error || JSON.stringify(errBody);
                } catch (e) { errMsg = resp.statusText; }
                console.warn('[App] enrichUser HTTP', resp.status, errMsg);
                return false;
            }
            const data = await resp.json();
            if (data.success && data.user) {
                const u = data.user;
                const merged = {
                    ...existing,
                    uid: u.uid, name: u.name, email: u.email,
                    phone: u.phone || '',
                    street: u.street || '',
                    street2: u.street2 || '',
                    city: u.city || '',
                    zip: u.zip || '',
                    admin_phone: u.admin_phone || '',
                    company_name: u.company_name || u.name,
                    zone: u.zone || '',
                    note_moyenne: u.note_moyenne || 0,
                    interventions: u.interventions || 0,
                    ca_total: u.ca_total || 0,
                    ca_mois: u.ca_mois || 0,
                    solde_comptabilite: u.solde_comptabilite ?? null,
                    taux_acceptation: u.taux_acceptation ?? null,
                    factures_a_fournir: u.factures_a_fournir ?? 0,
                    specialites: u.specialites || [],
                    specialites_types: u.specialites_types || [],
                    membre_depuis: u.membre_depuis || '',
                    certifications: u.certifications || [],
                    intervenant_id: u.intervenant_id,
                };
                localStorage.setItem('ss_user', JSON.stringify(merged));
                Auth.loadFromStorage();
                return true;
            }
        } catch(e) { console.warn('[App] enrichUser:', e); }
        return false;
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
        set('statInterventions', nbInterv);

        if (window.Dashboard && typeof Dashboard.updateExtendedStats === 'function') {
            Dashboard.updateExtendedStats(user);
        } else {
            const soldeEl = document.getElementById('statSolde');
            if (soldeEl && user.solde_comptabilite != null) {
                const s = user.solde_comptabilite;
                soldeEl.textContent = Math.abs(s).toLocaleString('fr-FR', { minimumFractionDigits: 2, maximumFractionDigits: 2 }) + ' €';
                soldeEl.className = 'stat-value ' + (s < 0 ? 'stat-solde-debit' : 'stat-solde-credit');
            }
            const tauxEl = document.getElementById('statTauxAccept');
            if (tauxEl) {
                tauxEl.textContent = user.taux_acceptation != null
                    ? user.taux_acceptation + ' %'
                    : '—';
            }
            const factEl = document.getElementById('statFacturesAFournir');
            if (factEl) factEl.textContent = user.factures_a_fournir ?? 0;
        }

        // Profil
        set('profileAvatarLg', initials || '?');
        set('profileNameLg', name);
        set('profileCompanyLg', company);
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

        if (window.Profile && typeof Profile.loadFromUser === 'function') {
            Profile.loadFromUser();
        }
    }

    function _restoreUserSession(fallbackUser) {
        let user = {};
        try { user = JSON.parse(localStorage.getItem('ss_user') || '{}'); } catch(e) {}
        if (!user.name && fallbackUser && fallbackUser.name) {
            const restored = { ...fallbackUser, ...user };
            localStorage.setItem('ss_user', JSON.stringify(restored));
            Auth.loadFromStorage();
        }
        _updateUIFromUser();
    }

    function _handleSWMessage(data) {
        if (!data || !data.type) return;
        const missionId = data.missionId || data.mission_id;

        if (data.type === 'OPEN_MISSION' && missionId && window.MissionDetail) {
            MissionDetail.open(missionId);
            return;
        }
        if (data.type === 'MISSION_ACCEPTED') {
            Toast.show('✅ Mission acceptée — disponible dans Mes Missions', 'success');
            if (window.Dashboard) Dashboard.refresh();
            if (missionId && window.MissionDetail) MissionDetail.open(missionId);
            return;
        }
        if (data.type === 'MISSION_REFUSED') {
            Toast.show('Mission refusée', 'info');
            if (window.Dashboard) Dashboard.refresh();
            return;
        }
        if (data.type === 'MISSION_ACTION_ERROR') {
            Toast.show(data.message || 'Action impossible depuis la notification', 'error', 8000);
        }
    }

    async function _registerSW() {
        if (!('serviceWorker' in navigator)) return;
        try {
            const reg = await navigator.serviceWorker.register(CONFIG.SW_PATH, { scope: '/sinistre_services/static/pwa/' });
            console.log('[SW] Enregistré:', reg.scope);

            try {
                const storedToken = localStorage.getItem('ss_fcm_token');
                const sw = reg.active || reg.waiting || reg.installing;
                if (storedToken && sw) {
                    sw.postMessage({ type: 'FCM_TOKEN', token: storedToken });
                }
            } catch (e) { /* ignore */ }

            // Écouter les messages du SW
            navigator.serviceWorker.addEventListener('message', (e) => {
                _handleSWMessage(e.data);
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
        const fallbackUser = Auth.getUser() || (() => {
            try { return JSON.parse(localStorage.getItem('ss_user') || '{}'); } catch(e) { return {}; }
        })();
        _enrichUserFromAPI().finally(() => {
            _restoreUserSession(fallbackUser);
            showView('dashboard', document.getElementById('nav-dashboard'));
        });

        // Deep link : ouvrir ou répondre à une mission depuis push
        const urlParams = new URLSearchParams(window.location.search);
        const missionId = urlParams.get('mission');
        const pushAction = urlParams.get('action');
        if (missionId && pushAction === 'accept' && window.Dashboard) {
            Dashboard.accepterMission(Number(missionId), null);
        } else if (missionId && pushAction === 'refuse' && window.Dashboard) {
            Dashboard.refuserMission(Number(missionId), null, true);
        } else if (missionId) {
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
        if (splash) { splash.classList.add('hidden'); setTimeout(() => { splash.style.display = 'none'; }, 400); }
        const app = document.getElementById('app');
        if (app) app.style.display = 'flex';
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
        if (viewId === 'dashboard') {
            if (window.Dashboard) Dashboard.init();
            else console.error('[App] Dashboard non chargé — vérifiez dashboard.js (Network)');
            _updateUIFromUser();
        }
        if (viewId === 'profile') {
            _enrichUserFromAPI().finally(() => {
                _restoreUserSession(Auth.getUser());
            });
        }
        if (viewId === 'missions') {
            if (window.Dashboard) Dashboard.loadMissions();
        }
        if (viewId === 'interventions') {
            if (window.Dashboard) Dashboard.loadInterventions();
        }
        if (viewId === 'carte') {
            // setTimeout 300ms pour laisser le DOM se mettre à jour
            setTimeout(function() {
                console.log('[App] Appel CarteMap.init()');
                if (window.CarteMap) CarteMap.init();
                else console.error('[App] CarteMap non défini !');
            }, 300);
        }
        if (viewId === 'planning') {
            setTimeout(function() {
                if (window.Planning) Planning.init();
            }, 100);
        }
        if (viewId === 'comptabilite') {
            setTimeout(function() {
                if (window.Comptabilite) Comptabilite.init();
            }, 100);
        }
    }

    function showSubView(viewId) {
        document.querySelectorAll('.view-page').forEach(function(v) { v.classList.remove('active'); });
        var target = document.getElementById('view-' + viewId);
        if (target) target.classList.add('active');
        _history.push(_currentView);
        _currentView = viewId;
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
            if (window.Dashboard) Dashboard.refresh();
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
        showSubView,
        goBack,
        _handleSWMessage,
        get currentView() { return _currentView; },
    };
})();

/* ══════════════════════════════════════════════════════════════
   Module Planning — Heures d'ouverture + Absences
══════════════════════════════════════════════════════════════ */
window.Planning = (function() {
    'use strict';

    const DAYS   = ['DIM','LUN','MAR','MER','JEU','VEN','SAM'];
    const HOURS  = Array.from({length: 24}, (_, i) => i); // 0h → 23h

    // État local : slots[jour][heure] = true/false (jour 0=dim, 1=lun…)
    let _slots = {};

    function _defaultSlots() {
        const s = {};
        for (let d = 0; d < 7; d++) {
            s[d] = {};
            for (let h = 0; h < 24; h++) s[d][h] = true;
        }
        return s;
    }

    function _normalizeSlots(raw) {
        const out = {};
        for (let d = 0; d < 7; d++) {
            const srcDay = (raw && (raw[d] || raw[String(d)])) || {};
            out[d] = {};
            for (let h = 0; h < 24; h++) {
                out[d][h] = !!(srcDay[h] ?? srcDay[String(h)]);
            }
        }
        return out;
    }

    function init() {
        // Charger depuis l'API ou utiliser des défauts
        API.get('/intervenant/planning')
            .then(function(data) {
                _slots = _normalizeSlots(data.slots || _defaultSlots());
                _render();
                _renderAbsences(data.absences || []);
            })
            .catch(function() {
                _slots = _defaultSlots();
                _render();
            });
    }

    function _render() {
        const tbody = document.getElementById('planningBody');
        if (!tbody) return;
        tbody.innerHTML = '';

        HOURS.forEach(function(h) {
            const tr = document.createElement('tr');
            tr.innerHTML = '<td style="padding:4px 8px;font-size:12px;color:#6B7280;white-space:nowrap;">' + h + ' H</td>';
            // LUN=1, MAR=2 … SAM=6, DIM=0
            [1,2,3,4,5,6,0].forEach(function(d) {
                const checked = _slots[d] && _slots[d][h] ? 'checked' : '';
                tr.innerHTML += '<td style="text-align:center;padding:3px;">'
                    + '<input type="checkbox" ' + checked
                    + ' onchange="Planning.toggleSlot(' + d + ',' + h + ',this.checked)"'
                    + ' style="accent-color:#1E40AF;width:15px;height:15px;cursor:pointer;"/></td>';
            });
            tbody.appendChild(tr);
        });

        // Mettre à jour les checkboxes "Tout" selon l'état réel
        document.querySelectorAll('.planning-day-all').forEach(function(cb) {
            const d = parseInt(cb.dataset.day);
            cb.checked = Object.values(_slots[d] || {}).every(Boolean);
        });
    }

    function toggleSlot(day, hour, val) {
        if (!_slots[day]) _slots[day] = {};
        _slots[day][hour] = val;
        // Mettre à jour la checkbox "Tout" pour ce jour
        const allCb = document.querySelector('.planning-day-all[data-day="' + day + '"]');
        if (allCb) allCb.checked = Object.values(_slots[day]).every(Boolean);
    }

    function toggleDay(day, val) {
        if (!_slots[day]) _slots[day] = {};
        for (let h = 0; h < 24; h++) _slots[day][h] = val;
        _render();
    }

    function save() {
        API.post('/intervenant/planning', { slots: _slots })
            .then(function() { Toast.show('Planning enregistré', 'success'); })
            .catch(function() { Toast.show('Erreur lors de l\'enregistrement', 'error'); });
    }

    function addAbsence() {
        var from = document.getElementById('absenceFrom')?.value;
        var to   = document.getElementById('absenceTo')?.value;
        if (!from || !to) { Toast.show('Veuillez saisir les deux dates', 'error'); return; }
        if (to < from)    { Toast.show('La date de fin doit être après la date de début', 'error'); return; }
        API.post('/intervenant/absences', { date_debut: from, date_fin: to })
            .then(function(data) {
                Toast.show('Absence enregistrée', 'success');
                document.getElementById('absenceFrom').value = '';
                document.getElementById('absenceTo').value   = '';
                _renderAbsences(data.absences || []);
            })
            .catch(function() { Toast.show('Erreur lors de l\'enregistrement', 'error'); });
    }

    function _renderAbsences(absences) {
        var list = document.getElementById('absenceList');
        if (!list) return;
        if (!absences.length) {
            list.innerHTML = '<p style="font-size:13px;color:#9CA3AF;text-align:center;padding:16px 0;">Aucune absence en cours ou à venir</p>';
            return;
        }
        list.innerHTML = absences.map(function(a) {
            return '<div style="display:flex;justify-content:space-between;align-items:center;padding:10px 14px;background:#F9FAFB;border:1px solid #E5E7EB;border-radius:8px;margin-bottom:8px;font-size:13px;">'
                + '<span>Du <strong>' + a.date_debut + '</strong> au <strong>' + a.date_fin + '</strong></span>'
                + '<button onclick="Planning.removeAbsence(' + a.id + ')" style="background:none;border:none;color:#EF4444;cursor:pointer;font-size:16px;" title="Supprimer">×</button>'
                + '</div>';
        }).join('');
    }

    function removeAbsence(id) {
        API.post('/intervenant/absences/delete', { id: id })
            .then(function(data) {
                Toast.show('Absence supprimée', 'success');
                _renderAbsences(data.absences || []);
            })
            .catch(function() { Toast.show('Erreur lors de la suppression', 'error'); });
    }

    return { init, toggleSlot, toggleDay, save, addAbsence, removeAbsence };
})();
