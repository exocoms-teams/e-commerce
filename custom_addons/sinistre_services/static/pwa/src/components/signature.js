/**
 * signature.js — Signature tactile multi-usage
 *
 * Modes :
 *   'devis'          → acceptation devis (signature initiale)
 *   'devis_modifie'  → re-signature après modification devis en cours d'intervention
 *   'avant'          → signature client AVANT démarrage intervention
 *   'apres'          → signature client APRÈS intervention (déclenche facturation)
 */

window.Signature = (() => {
    let _canvas       = null;
    let _ctx          = null;
    let _drawing      = false;
    let _hasContent   = false;
    let _mode         = null;   // 'devis' | 'devis_modifie' | 'avant' | 'apres'
    let _devisId      = null;
    let _missionId    = null;

    /* ── Init canvas ── */
    function init() {
        _canvas = document.getElementById('signatureCanvas');
        if (!_canvas) return;
        const wrap = _canvas.parentElement;
        _canvas.width  = wrap.clientWidth || 320;
        _canvas.height = 200;
        _ctx = _canvas.getContext('2d');
        _ctx.strokeStyle = '#1A1A2E';
        _ctx.lineWidth   = 2.5;
        _ctx.lineCap     = 'round';
        _ctx.lineJoin    = 'round';
        _hasContent = false;
        document.getElementById('signPlaceholder')?.classList.remove('hidden');
        _bindEvents();
    }

    function _getPos(e) {
        const rect  = _canvas.getBoundingClientRect();
        const touch = e.touches ? e.touches[0] : e;
        return {
            x: (touch.clientX - rect.left) * (_canvas.width  / rect.width),
            y: (touch.clientY - rect.top)  * (_canvas.height / rect.height),
        };
    }

    function _bindEvents() {
        _canvas.onmousedown  = (e) => { _drawing = true; const p = _getPos(e); _ctx.beginPath(); _ctx.moveTo(p.x, p.y); };
        _canvas.onmousemove  = (e) => { if (!_drawing) return; const p = _getPos(e); _ctx.lineTo(p.x, p.y); _ctx.stroke(); _showContent(); };
        _canvas.onmouseup    = () => { _drawing = false; };
        _canvas.onmouseleave = () => { _drawing = false; };
        _canvas.addEventListener('touchstart', (e) => { e.preventDefault(); _drawing = true; const p = _getPos(e); _ctx.beginPath(); _ctx.moveTo(p.x, p.y); }, { passive: false });
        _canvas.addEventListener('touchmove',  (e) => { e.preventDefault(); if (!_drawing) return; const p = _getPos(e); _ctx.lineTo(p.x, p.y); _ctx.stroke(); _showContent(); }, { passive: false });
        _canvas.addEventListener('touchend',   () => { _drawing = false; });
    }

    function _showContent() {
        if (!_hasContent) {
            _hasContent = true;
            document.getElementById('signPlaceholder')?.classList.add('hidden');
        }
    }

    function getBase64() { return _canvas.toDataURL('image/png').split(',')[1]; }
    function isEmpty() {
        if (!_hasContent) return true;
        const d = _ctx.getImageData(0, 0, _canvas.width, _canvas.height).data;
        return !d.some((v, i) => i % 4 !== 3 && v !== 0);
    }

    /* ── Titres / sous-titres selon mode ── */
    function _labels(mode) {
        switch (mode) {
            case 'devis':
                return { title: 'Signature Devis', sub: 'Le client signe pour accepter le devis' };
            case 'devis_modifie':
                return { title: 'Re-Signature Devis Modifié', sub: '⚠️ Le devis a été modifié. Le client doit signer à nouveau avant la reprise des travaux.' };
            case 'avant':
                return { title: 'Signature Avant Intervention', sub: 'Le client signe pour autoriser le démarrage des travaux' };
            case 'apres':
                return { title: 'Signature Après Intervention', sub: 'Le client signe pour valider la bonne exécution des travaux' };
            default:
                return { title: 'Signature', sub: '' };
        }
    }

    /* ── Ouvrir le pad ── */
    function open(opts) {
        /* opts : { mode, missionId, devisId? } */
        _mode      = opts.mode || 'avant';
        _missionId = opts.missionId;
        _devisId   = opts.devisId || null;

        App.showView('signature', 'Signature');
        requestAnimationFrame(() => {
            init();
            const lbl = _labels(_mode);
            const titleEl = document.getElementById('signatureTitle');
            const subEl   = document.getElementById('signatureSub');
            if (titleEl) titleEl.textContent = lbl.title;
            if (subEl)   subEl.textContent   = lbl.sub;

            // Boutons contextuels
            const btnConfirm = document.getElementById('btnSignConfirm');
            const btnRefuse  = document.getElementById('btnSignRefuse');
            if (btnConfirm) {
                const labels = {
                    devis:          '✅ Confirmer l\'acceptation',
                    devis_modifie:  '✅ Accepter le devis modifié',
                    avant:          '✅ Autoriser le démarrage',
                    apres:          '✅ Valider la fin d\'intervention',
                };
                btnConfirm.textContent = labels[_mode] || '✅ Confirmer';
            }
            if (btnRefuse) {
                btnRefuse.style.display = ['devis', 'devis_modifie'].includes(_mode) ? 'flex' : 'none';
            }
        });
    }

    /* ── Confirmer (dispatch selon mode) ── */
    async function confirm() {
        if (isEmpty()) { Toast.show('Le client doit signer avant de confirmer', 'warning'); return; }
        const sig = getBase64();
        switch (_mode) {
            case 'devis':          return _confirmDevis(sig, false);
            case 'devis_modifie':  return _confirmDevis(sig, true);
            case 'avant':          return _confirmAvant(sig);
            case 'apres':          return _confirmApres(sig);
        }
    }

    async function _confirmDevis(sig, isModified) {
        try {
            await Offline.tryOrQueue(
                isModified ? 'RESIGNATURE_DEVIS' : 'ACCEPTER_DEVIS',
                () => API.accepterDevis(_devisId, sig, isModified),
                { devisId: _devisId, signature: sig, isModified }
            );
            Toast.show(isModified ? '✅ Devis modifié accepté' : '✅ Devis accepté', 'success');
            App.showView('mission', 'Mission');
            MissionDetail.reload();
        } catch (err) { Toast.show('Erreur: ' + err.message, 'error'); }
    }

    async function _confirmAvant(sig) {
        try {
            await Offline.tryOrQueue(
                'SIGNATURE_AVANT',
                () => API.signerAvant(_missionId, sig),
                { missionId: _missionId, signature: sig }
            );
            Toast.show('✅ Signature avant enregistrée — vous pouvez démarrer', 'success');
            App.showView('mission', 'Mission');
            MissionDetail.reload();
        } catch (err) { Toast.show('Erreur: ' + err.message, 'error'); }
    }

    async function _confirmApres(sig) {
        try {
            await Offline.tryOrQueue(
                'SIGNATURE_APRES',
                () => API.signerApres(_missionId, sig),
                { missionId: _missionId, signature: sig }
            );
            Toast.show('✅ Intervention validée — facture générée', 'success');
            App.showView('mission', 'Mission');
            MissionDetail.reload();
        } catch (err) { Toast.show('Erreur: ' + err.message, 'error'); }
    }

    async function refuse() {
        if (!confirm('Confirmer le refus du devis par le client ?')) return;
        try {
            await Offline.tryOrQueue(
                'REFUSER_DEVIS',
                () => API.refuserDevis(_devisId),
                { devisId: _devisId }
            );
            Toast.show('Devis refusé enregistré', 'warning');
            App.showView('mission', 'Mission');
            MissionDetail.reload();
        } catch (err) { Toast.show('Erreur: ' + err.message, 'error'); }
    }

    return {
        init,
        open,
        confirm,
        refuse,
        clear() {
            if (!_ctx) return;
            _ctx.clearRect(0, 0, _canvas.width, _canvas.height);
            _hasContent = false;
            document.getElementById('signPlaceholder')?.classList.remove('hidden');
        },
        /* Rétrocompat — ancienne API open(devisId, missionId) */
        openDevis(devisId, missionId) {
            this.open({ mode: 'devis', devisId, missionId });
        },
    };
})();
