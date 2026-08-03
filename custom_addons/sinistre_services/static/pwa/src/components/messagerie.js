/**
 * messagerie.js — Messagerie Artisan ↔ Plateforme
 *
 * Fonctions :
 *  - Afficher le fil de messages d'une mission
 *  - Envoyer un message (texte)
 *  - Badge non-lus sur l'onglet mission
 */

window.Messagerie = (() => {
    let _missionId = null;
    let _messages  = [];
    let _pollTimer = null;

    /* ── Ouvrir l'écran messagerie ── */
    function open(missionId) {
        _missionId = missionId;
        App.showView('messagerie', '💬 Messages');
        _load();
        _startPolling();
    }

    /* ── Charger les messages ── */
    async function _load() {
        try {
            const data = await API.getMessages(_missionId);
            _messages  = data.messages || [];
            _render();
        } catch (err) {
            Toast.show('Impossible de charger les messages', 'error');
        }
    }

    /* ── Rendu ── */
    function _render() {
        const container = document.getElementById('messagerieList');
        if (!container) return;
        container.innerHTML = '';

        if (!_messages.length) {
            container.innerHTML = '<p style="text-align:center;color:#9CA3AF;padding:32px 0;font-size:13px">Aucun message pour l\'instant</p>';
            return;
        }

        _messages.forEach(msg => {
            const isMe = msg.auteur_type === 'artisan';
            const authorLabel = isMe
                ? 'Moi'
                : (msg.auteur_type === 'assurance'
                    ? '🛡 Assurance'
                    : (msg.auteur_nom || '🏢 Plateforme'));
            const div  = document.createElement('div');
            div.className = `msg-bubble ${isMe ? 'msg-me' : 'msg-other'}`;
            div.innerHTML = `
                <div class="msg-author">${authorLabel}</div>
                <div class="msg-text">${_escapeHtml(msg.contenu)}</div>
                <div class="msg-date">${_formatDate(msg.date_envoi)}</div>
            `;
            container.appendChild(div);
        });

        // Scroll au bas
        container.scrollTop = container.scrollHeight;

        // Marquer comme lu
        API.marquerLu(_missionId).catch(() => {});
        _updateBadge(0);
    }

    /* ── Envoyer un message ── */
    async function send() {
        const input = document.getElementById('messagerieInput');
        if (!input) return;
        const texte = input.value.trim();
        if (!texte) { Toast.show('Écrivez un message', 'warning'); return; }

        input.value    = '';
        input.disabled = true;
        try {
            const data = await API.sendMessage(_missionId, texte);
            _messages.push(data.message || { auteur_type: 'artisan', contenu: texte, date_envoi: new Date().toISOString() });
            _render();
        } catch (err) {
            Toast.show('Erreur envoi: ' + err.message, 'error');
            input.value = texte;
        } finally {
            input.disabled = false;
            input.focus();
        }
    }

    /* ── Polling (toutes les 30 s) ── */
    function _startPolling() {
        _stopPolling();
        _pollTimer = setInterval(() => {
            if (document.getElementById('view-messagerie')?.classList.contains('active')) {
                _load();
            }
        }, 30000);
    }

    function _stopPolling() {
        if (_pollTimer) { clearInterval(_pollTimer); _pollTimer = null; }
    }

    /* ── Badge non-lus ── */
    function _updateBadge(count) {
        const badge = document.getElementById('msgBadge');
        if (!badge) return;
        badge.textContent = count || '';
        badge.style.display = count ? 'flex' : 'none';
    }

    function updateUnreadBadge(count) { _updateBadge(count); }

    /* ── Helpers ── */
    function _escapeHtml(s) {
        return String(s)
            .replace(/&/g,'&amp;').replace(/</g,'&lt;').replace(/>/g,'&gt;')
            .replace(/\n/g,'<br>');
    }
    function _formatDate(dt) {
        if (!dt) return '';
        return new Date(dt).toLocaleString('fr-FR', { day:'2-digit', month:'2-digit', hour:'2-digit', minute:'2-digit' });
    }

    return { open, send, updateUnreadBadge, stopPolling: _stopPolling };
})();
