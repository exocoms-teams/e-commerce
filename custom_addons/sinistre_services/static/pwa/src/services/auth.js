/**
 * auth.js — Gestion de l'authentification
 * Stocke la session en localStorage, vérifie à chaque démarrage
 */

window.Auth = (() => {
    const KEY_USER = 'ss_user';
    let _user = null;

    return {
        /* ── Getters ── */
        getUser() { return _user; },
        isLoggedIn() { return !!_user; },

        /* ── Charger depuis localStorage ── */
        loadFromStorage() {
            try {
                const raw = localStorage.getItem(KEY_USER);
                if (raw) _user = JSON.parse(raw);
            } catch { _user = null; }
            return _user;
        },

        /* ── Login ── */
        async login(email, password) {
            const loginBtn = document.getElementById('loginBtn');
            const errorEl  = document.getElementById('loginError');
            errorEl.style.display = 'none';
            loginBtn.disabled = true;
            loginBtn.innerHTML = '<span>Connexion…</span>';

            try {
                const result = await API.login(email, password);
                _user = {
                    uid:   result.user.uid,
                    name:  result.user.name,
                    email: result.user.username,
                    lang:  result.user.lang,
                };
                localStorage.setItem(KEY_USER, JSON.stringify(_user));
                Toast.show(`Bienvenue ${_user.name} 👋`, 'success');
                App.showApp();
            } catch (err) {
                errorEl.textContent = err.message || 'Connexion impossible';
                errorEl.style.display = 'block';
            } finally {
                loginBtn.disabled = false;
                loginBtn.innerHTML = '<span>Se connecter</span>';
            }
        },

        /* ── Vérifier session active ── */
        async verify() {
            if (!_user) return false;
            try {
                const session = await API.getSession();
                return !!(session && session.uid);
            } catch {
                return false;
            }
        },

        /* ── Logout ── */
        async logout() {
            try { await API.logout(); } catch {}
            _user = null;
            localStorage.removeItem(KEY_USER);
            App.showLogin();
            Toast.show('Déconnexion réussie');
        },
    };
})();

/* ── Gestion du formulaire de login ── */
document.getElementById('loginForm').addEventListener('submit', async (e) => {
    e.preventDefault();
    const email    = document.getElementById('loginEmail').value.trim();
    const password = document.getElementById('loginPassword').value;
    await Auth.login(email, password);
});
