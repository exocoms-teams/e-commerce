/**
 * signature.js — Signature client sur canvas tactile
 * Utilisé pour l'acceptation du devis
 */

window.Signature = (() => {
    let _canvas = null;
    let _ctx = null;
    let _drawing = false;
    let _hasContent = false;
    let _currentDevisId = null;
    let _currentMissionId = null;

    function init() {
        _canvas = document.getElementById('signatureCanvas');
        if (!_canvas) return;

        // Adapter la taille du canvas à son conteneur
        const wrap = _canvas.parentElement;
        _canvas.width  = wrap.clientWidth  || 320;
        _canvas.height = 200;

        _ctx = _canvas.getContext('2d');
        _ctx.strokeStyle = '#1A1A2E';
        _ctx.lineWidth   = 2.5;
        _ctx.lineCap     = 'round';
        _ctx.lineJoin    = 'round';

        _bindEvents();
    }

    function _getPos(e) {
        const rect = _canvas.getBoundingClientRect();
        const touch = e.touches ? e.touches[0] : e;
        return {
            x: (touch.clientX - rect.left) * (_canvas.width / rect.width),
            y: (touch.clientY - rect.top)  * (_canvas.height / rect.height),
        };
    }

    function _bindEvents() {
        // Mouse
        _canvas.addEventListener('mousedown', (e) => {
            _drawing = true;
            const pos = _getPos(e);
            _ctx.beginPath();
            _ctx.moveTo(pos.x, pos.y);
        });
        _canvas.addEventListener('mousemove', (e) => {
            if (!_drawing) return;
            const pos = _getPos(e);
            _ctx.lineTo(pos.x, pos.y);
            _ctx.stroke();
            _showContent();
        });
        _canvas.addEventListener('mouseup', ()   => { _drawing = false; });
        _canvas.addEventListener('mouseleave', () => { _drawing = false; });

        // Touch
        _canvas.addEventListener('touchstart', (e) => {
            e.preventDefault();
            _drawing = true;
            const pos = _getPos(e);
            _ctx.beginPath();
            _ctx.moveTo(pos.x, pos.y);
        }, { passive: false });
        _canvas.addEventListener('touchmove', (e) => {
            e.preventDefault();
            if (!_drawing) return;
            const pos = _getPos(e);
            _ctx.lineTo(pos.x, pos.y);
            _ctx.stroke();
            _showContent();
        }, { passive: false });
        _canvas.addEventListener('touchend', () => { _drawing = false; });
    }

    function _showContent() {
        if (!_hasContent) {
            _hasContent = true;
            document.getElementById('signPlaceholder')?.classList.add('hidden');
        }
    }

    function getBase64() {
        return _canvas.toDataURL('image/png').split(',')[1];
    }

    function isEmpty() {
        if (!_hasContent) return true;
        // Vérification pixel : si tous les pixels sont blancs/transparents
        const imageData = _ctx.getImageData(0, 0, _canvas.width, _canvas.height);
        return !imageData.data.some((val, i) => i % 4 !== 3 && val !== 0);
    }

    return {
        init,

        open(devisId, missionId) {
            _currentDevisId    = devisId;
            _currentMissionId  = missionId;
            App.showView('signature', 'Signature Client');
            // Init après render
            requestAnimationFrame(() => init());
        },

        clear() {
            if (!_ctx) return;
            _ctx.clearRect(0, 0, _canvas.width, _canvas.height);
            _hasContent = false;
            document.getElementById('signPlaceholder')?.classList.remove('hidden');
        },

        async confirm() {
            if (isEmpty()) {
                Toast.show('Le client doit signer avant de confirmer', 'warning');
                return;
            }

            const signature = getBase64();

            try {
                await Offline.tryOrQueue(
                    'ACCEPTER_DEVIS',
                    () => API.accepterDevis(_currentDevisId, signature),
                    { devisId: _currentDevisId, signature }
                );
                Toast.show('✅ Devis accepté — vous pouvez démarrer', 'success');
                App.showView('mission', 'Mission');
                MissionDetail.reload();
            } catch (err) {
                Toast.show('Erreur: ' + err.message, 'error');
            }
        },

        async refuse() {
            if (!confirm('Confirmer le refus du devis par le client ?')) return;

            try {
                await Offline.tryOrQueue(
                    'REFUSER_DEVIS',
                    () => API.refuserDevis(_currentDevisId),
                    { devisId: _currentDevisId }
                );
                Toast.show('Devis refusé enregistré', 'warning');
                App.showView('mission', 'Mission');
                MissionDetail.reload();
            } catch (err) {
                Toast.show('Erreur: ' + err.message, 'error');
            }
        },
    };
})();
