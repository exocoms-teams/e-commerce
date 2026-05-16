/**
 * mission_detail.js — Écran de détail d'une mission
 * Gère : photos, devis, actions workflow, suivi état
 */

window.MissionDetail = (() => {
    let _mission     = null;
    let _missionId   = null;
    let _isLoading   = false;

    /* ── Ouvrir une mission ── */
    async function open(idOrRef) {
        _missionId = idOrRef;
        App.showView('mission', 'Chargement…');
        await _load();
    }

    async function _load() {
        if (_isLoading) return;
        _isLoading = true;
        try {
            const data = await API.getMission(_missionId);
            _mission   = data.mission || data;
            Photos.setMission(_mission.id);
            _render();
        } catch (err) {
            Toast.show('Impossible de charger la mission', 'error');
            App.goBack();
        } finally {
            _isLoading = false;
        }
    }

    function _render() {
        if (!_mission) return;

        const m = _mission;
        document.getElementById('topbarTitle').textContent = m.reference || 'Mission';

        // ── Status banner ──
        const state = CONFIG.STATE_LABELS[m.state] || { label: m.state, icon: '❓' };
        const urgConf = CONFIG.URGENCE_COLORS[m.urgence] || CONFIG.URGENCE_COLORS.normale;
        const banner = document.getElementById('missionBanner');
        banner.style.background = urgConf.bg;
        banner.style.color      = urgConf.text;
        document.getElementById('missionBannerIcon').textContent = state.icon;
        document.getElementById('missionBannerText').textContent = state.label;

        // ── Client ──
        document.getElementById('clientInfo').innerHTML = `
            <div class="info-item">
                <div class="info-label">Client</div>
                <div class="info-val">${m.client || '–'}</div>
            </div>
            <div class="info-item">
                <div class="info-label">Source</div>
                <div class="info-val">${_sourceLabel(m.source)}</div>
            </div>
            <div class="info-item info-val full-width" style="grid-column:1/-1">
                <div class="info-label">Téléphone sur place</div>
                <div class="info-val">
                    ${m.tel_sur_place
                        ? `<a href="tel:${m.tel_sur_place}" style="color:var(--blue); font-weight:600">${m.tel_sur_place}</a>`
                        : '–'}
                </div>
            </div>
        `;

        // ── Intervention ──
        document.getElementById('interventionInfo').innerHTML = `
            <div class="info-item">
                <div class="info-label">Type</div>
                <div class="info-val">${CONFIG.TYPE_LABELS[m.type_intervention] || m.type_intervention}</div>
            </div>
            <div class="info-item">
                <div class="info-label">Urgence</div>
                <div class="info-val" style="color:${urgConf.text}">${urgConf.icon} ${m.urgence}</div>
            </div>
            <div class="info-item" style="grid-column:1/-1">
                <div class="info-label">Adresse</div>
                <div class="info-val">
                    <a href="https://maps.google.com/?q=${encodeURIComponent(m.adresse || '')}"
                       target="_blank" style="color:var(--blue)">
                        📍 ${m.adresse || '–'}
                    </a>
                </div>
            </div>
            ${m.date_rdv ? `
            <div class="info-item">
                <div class="info-label">Date RDV</div>
                <div class="info-val">${_formatDate(m.date_rdv)}</div>
            </div>` : ''}
            ${m.montant_devis ? `
            <div class="info-item">
                <div class="info-label">Montant Devis</div>
                <div class="info-val" style="font-weight:700;color:var(--blue)">${_fmt(m.montant_devis)} €</div>
            </div>
            <div class="info-item">
                <div class="info-label">Reste à charge</div>
                <div class="info-val" style="font-weight:700">${_fmt(m.reste_a_charge)} €</div>
            </div>` : ''}
        `;

        // ── Description ──
        document.getElementById('descriptionText').textContent = m.description || '–';

        // ── Photos ──
        _renderPhotos(m);

        // ── Devis ──
        _renderDevis(m);

        // ── Actions ──
        _renderActions(m);
    }

    /* ── Photos ── */
    function _renderPhotos(m) {
        const grid   = document.getElementById('photosGrid');
        const counts = document.getElementById('photoCounts');
        grid.innerHTML = '';

        const avant = (m.photos || []).filter(p => p.type_photo === 'avant');
        const apres = (m.photos || []).filter(p => p.type_photo === 'apres');

        counts.textContent = `${avant.length} avant · ${apres.length} après`;

        [...avant, ...apres].forEach(photo => {
            const thumb = document.createElement('div');
            thumb.className = `photo-thumb ${photo.type_photo}`;
            thumb.innerHTML = `
                <img src="${photo.url || photo.image_url || '#'}"
                     alt="Photo ${photo.type_photo}"
                     onerror="this.style.display='none'"/>
                <div class="photo-thumb-label">${photo.type_photo}</div>
            `;
            grid.appendChild(thumb);
        });

        // Boutons photo
        const btnAvant = document.getElementById('btnPhotoAvant');
        const btnApres = document.getElementById('btnPhotoApres');
        const state = m.state;
        btnAvant.style.display = ['nouveau','assigne','rdv_planifie','en_cours'].includes(state) ? 'flex' : 'none';
        btnApres.style.display = ['en_cours','travaux_en_cours','devis_accepte'].includes(state) ? 'flex' : 'none';
    }

    function addPhotoThumb({ type, preview }) {
        const grid  = document.getElementById('photosGrid');
        const thumb = document.createElement('div');
        thumb.className = `photo-thumb ${type}`;
        thumb.innerHTML = `
            <img src="${preview}" alt="Photo ${type}"/>
            <div class="photo-thumb-label">${type}</div>
        `;
        grid.appendChild(thumb);
    }

    function refreshPhotoCounts() {
        if (_mission) {
            const avant = document.querySelectorAll('.photo-thumb.avant').length;
            const apres = document.querySelectorAll('.photo-thumb.apres').length;
            document.getElementById('photoCounts').textContent = `${avant} avant · ${apres} après`;
        }
    }

    /* ── Devis ── */
    function _renderDevis(m) {
        const card    = document.getElementById('devisCard');
        const content = document.getElementById('devisContent');
        const badge   = document.getElementById('devisStatusBadge');

        const devis = m.devis || null;

        if (!devis) {
            badge.style.display = 'none';
            const canCreate = ['en_cours','rdv_planifie','assigne'].includes(m.state);
            content.innerHTML = canCreate
                ? `<p style="color:var(--gray-mid);font-size:13px;margin-bottom:12px">Aucun devis créé</p>`
                : `<p style="color:var(--gray-mid);font-size:13px">–</p>`;
            return;
        }

        // Badge statut
        const devisStates = {
            brouillon: { label: 'Brouillon', color: 'var(--gray-mid)', bg: 'var(--gray-pale)' },
            envoye:    { label: 'Envoyé',    color: 'var(--orange)',   bg: 'var(--orange-pale)' },
            accepte:   { label: '✅ Accepté', color: 'var(--green)',   bg: 'var(--green-pale)' },
            refuse:    { label: '❌ Refusé',  color: 'var(--red)',     bg: 'var(--red-pale)' },
        };
        const ds = devisStates[devis.state] || devisStates.brouillon;
        badge.textContent   = ds.label;
        badge.style.color   = ds.color;
        badge.style.background = ds.bg;
        badge.style.display = 'inline-block';

        // Lignes devis
        const lignesHtml = (devis.lignes || []).map(l => `
            <div style="display:flex;justify-content:space-between;padding:6px 0;font-size:13px;border-bottom:1px solid var(--gray-border)">
                <span>${l.description} × ${l.quantite}</span>
                <span style="font-weight:600">${_fmt(l.montant_total)} €</span>
            </div>
        `).join('');

        content.innerHTML = `
            ${lignesHtml}
            <div style="display:flex;justify-content:space-between;margin-top:10px;font-family:var(--font-head);font-size:16px;font-weight:700;color:var(--blue)">
                <span>Total TTC</span>
                <span>${_fmt(devis.montant_total)} €</span>
            </div>
        `;
    }

    /* ── Actions workflow ── */
    function _renderActions(m) {
        const block = document.getElementById('missionActions');
        block.innerHTML = '';

        const state = m.state;

        // DÉMARRER (besoin photos avant)
        if (['rdv_planifie', 'assigne'].includes(state)) {
            const btn = _btn('🔧 Démarrer l\'intervention', 'btn-primary', async () => {
                const avant = document.querySelectorAll('.photo-thumb.avant').length;
                if (avant === 0) {
                    Toast.show('⚠️ Prenez des photos AVANT de démarrer', 'warning');
                    return;
                }
                await _action('DEMARRER_MISSION', () => API.demarrer(m.id), { missionId: m.id });
            });
            block.appendChild(btn);
        }

        // CRÉER DEVIS (si en cours et pas de devis)
        if (['en_cours', 'rdv_planifie'].includes(state) && !m.devis) {
            const btn = _btn('💶 Créer un devis', 'btn-outline', () => {
                DevisForm.open(m.id);
            });
            block.appendChild(btn);
        }

        // MODIFIER DEVIS (brouillon)
        if (m.devis?.state === 'brouillon') {
            const btn = _btn('✏️ Modifier le devis', 'btn-outline', () => {
                DevisForm.open(m.id, m.devis);
            });
            block.appendChild(btn);
        }

        // FAIRE SIGNER (devis envoyé)
        if (m.devis?.state === 'envoye') {
            const btnAccept = _btn('✅ Faire signer le client', 'btn-success', () => {
                Signature.open(m.devis.id, m.id);
            });
            const btnRefuse = _btn('❌ Client refuse', 'btn-danger', async () => {
                if (!confirm('Confirmer le refus ?')) return;
                await _action('REFUSER_DEVIS', () => API.refuserDevis(m.devis.id), { devisId: m.devis.id });
            });
            block.appendChild(btnAccept);
            block.appendChild(btnRefuse);
        }

        // TERMINER (besoin photos après)
        if (['devis_accepte', 'travaux_en_cours', 'en_cours'].includes(state)) {
            const btn = _btn('🎉 Terminer & clôturer', 'btn-success', async () => {
                const apres = document.querySelectorAll('.photo-thumb.apres').length;
                if (apres === 0) {
                    Toast.show('⚠️ Prenez des photos APRÈS les travaux', 'warning');
                    return;
                }
                if (!confirm('Confirmer la clôture de la mission ?')) return;
                await _action('TERMINER_MISSION', () => API.terminer(m.id), { missionId: m.id });
            });
            block.appendChild(btn);
        }

        // APPELER LE CLIENT
        if (m.tel_sur_place) {
            const btn = _btn(`📞 Appeler ${m.tel_sur_place}`, 'btn-outline', () => {
                window.location.href = `tel:${m.tel_sur_place}`;
            });
            block.appendChild(btn);
        }

        // NAVIGATION GPS
        if (m.adresse) {
            const btn = _btn('🗺 Ouvrir dans Maps', 'btn-outline', () => {
                window.open(`https://maps.google.com/?q=${encodeURIComponent(m.adresse)}`);
            });
            block.appendChild(btn);
        }
    }

    function _btn(label, cls, onClick) {
        const btn = document.createElement('button');
        btn.className = `btn ${cls} btn-block`;
        btn.innerHTML = `<span>${label}</span>`;
        btn.addEventListener('click', onClick);
        return btn;
    }

    async function _action(type, apiFn, queuePayload) {
        try {
            const result = await Offline.tryOrQueue(type, apiFn, queuePayload);
            if (!result?.queued) {
                Toast.show('Action enregistrée', 'success');
                await reload();
            }
        } catch (err) {
            Toast.show('Erreur: ' + err.message, 'error');
        }
    }

    /* ── Helpers ── */
    function _fmt(n) {
        return parseFloat(n || 0).toFixed(2).replace('.', ',');
    }

    function _formatDate(dt) {
        if (!dt) return '–';
        return new Date(dt).toLocaleDateString('fr-FR', {
            weekday: 'short', day: 'numeric', month: 'short',
            hour: '2-digit', minute: '2-digit',
        });
    }

    function _sourceLabel(s) {
        return { assurance: '🏢 Assurance', particulier: '👤 Particulier', entreprise: '🏭 Entreprise' }[s] || s;
    }

    /* ── API publique ── */
    return {
        open,
        reload: async () => await _load(),
        getMission: () => _mission,
        addPhotoThumb,
        refreshPhotoCounts,
    };
})();
