/**
 * mission_detail.js — Écran de détail d'une mission
 * Gère : photos, devis, actions workflow, suivi état
 */

window.MissionDetail = (() => {
    let _mission   = null;
    let _missionId = null;
    let _isLoading = false;

    /* ── Données demo pour fallback offline ── */
    const DEMO_MISSIONS = {
        1: { id: 1, reference: 'M-2026-0481', state: 'assigne', urgence: 'urgente',
             type_intervention: 'serrurerie', client: 'Mme Laurent', tel_sur_place: '+33 6 11 22 33 44',
             source: 'assurance', adresse: '12 rue de la République, Paris 11e',
             description: 'Cliente bloquée à l\'extérieur, porte 3 points classique. Clé cassée dans la serrure.',
             date_rdv: new Date(Date.now() + 2*3600000).toISOString(),
             montant_devis: null, reste_a_charge: null, photos: [], devis: null },
        2: { id: 2, reference: 'M-2026-0479', state: 'en_cours', urgence: 'normale',
             type_intervention: 'plomberie', client: 'M. Dubois', tel_sur_place: '+33 6 55 44 33 22',
             source: 'particulier', adresse: '45 av. Parmentier, Paris 11e',
             description: 'Joint siphon à remplacer, fuite active sous évier cuisine.',
             date_rdv: new Date(Date.now() + 4*3600000).toISOString(),
             montant_devis: 145, reste_a_charge: 0, photos: [], devis: null },
        3: { id: 3, reference: 'M-2026-0476', state: 'rdv_planifie', urgence: 'normale',
             type_intervention: 'electricite', client: 'SCI Belleville', tel_sur_place: '+33 1 40 00 11 22',
             source: 'entreprise', adresse: '8 rue des Pyrénées, Paris 20e',
             description: 'Remplacement tableau électrique 2 rangées. Mise aux normes NF C 15-100.',
             date_rdv: new Date(Date.now() + 86400000).toISOString(),
             montant_devis: 620, reste_a_charge: 120, photos: [], devis: null },
        4: { id: 4, reference: 'M-2026-0470', state: 'rdv_planifie', urgence: 'normale',
             type_intervention: 'chauffage', client: 'M. Karam', tel_sur_place: '+33 6 77 88 99 00',
             source: 'assurance', adresse: '23 bd Voltaire, Paris 11e',
             description: 'Plus d\'eau chaude, code erreur E01. Chaudière Saunier Duval Thema F25E.',
             date_rdv: new Date(Date.now() + 90000000).toISOString(),
             montant_devis: 220, reste_a_charge: 0, photos: [], devis: null },
        5: { id: 5, reference: 'M-2026-0468', state: 'en_cours', urgence: 'normale',
             type_intervention: 'vitrerie', client: 'Mme Petit', tel_sur_place: '+33 6 22 33 44 55',
             source: 'assurance', adresse: '7 rue Oberkampf, Paris 11e',
             description: 'Double vitrage 80×120 cm. Vitre brisée suite à tentative d\'effraction.',
             date_rdv: new Date(Date.now() + 5400000).toISOString(),
             montant_devis: 310, reste_a_charge: 60, photos: [], devis: null },
    };

    /* ── Ouvrir une mission ── */
    async function open(idOrRef) {
        // Convertir en entier si possible pour matcher la route /mission/<int>
        _missionId = (typeof idOrRef === 'string' && /^\d+$/.test(idOrRef)) ? parseInt(idOrRef) : idOrRef;
        App.showView('mission');
        await _load();
    }

    async function _load() {
        if (_isLoading) return;
        _isLoading = true;

        // Show loading state
        const banner = document.getElementById('missionBanner');
        if (banner) banner.textContent = 'Chargement…';

        try {
            const data = await API.getMission(_missionId);
            _mission = data.mission || data;
        } catch (err) {
            // Fallback: chercher dans les données demo
            const demo = DEMO_MISSIONS[_missionId] || Object.values(DEMO_MISSIONS).find(m => m.reference === _missionId);
            if (demo) {
                _mission = demo;
                Toast.show('Mode hors ligne — données en cache', 'warning');
            } else {
                Toast.show('Mission introuvable', 'error');
                App.goBack();
                _isLoading = false;
                return;
            }
        } finally {
            _isLoading = false;
        }

        Photos.setMission(_mission.id);
        _render();
    }

    function _render() {
        if (!_mission) return;
        const m = _mission;

        // Titre page (null-safe)
        const titleEl = document.getElementById('topbarTitle');
        if (titleEl) titleEl.textContent = m.reference || 'Mission';

        // ── Status banner ──
        const state   = CONFIG.STATE_LABELS[m.state] || { label: m.state, icon: '❓' };
        const urgConf = CONFIG.URGENCE_COLORS[m.urgence] || CONFIG.URGENCE_COLORS.normale;
        const banner  = document.getElementById('missionBanner');
        if (banner) {
            banner.style.background = urgConf.bg;
            banner.style.color      = urgConf.text;
        }
        const bi = document.getElementById('missionBannerIcon');
        const bt = document.getElementById('missionBannerText');
        if (bi) bi.textContent = state.icon;
        if (bt) bt.textContent = state.label;

        // ── Client ──
        const ci = document.getElementById('clientInfo');
        if (ci) ci.innerHTML = `
            <div class="info-item">
                <div class="info-label">Client</div>
                <div class="info-val">${m.client || '–'}</div>
            </div>
            <div class="info-item">
                <div class="info-label">Source</div>
                <div class="info-val">${_sourceLabel(m.source)}</div>
            </div>
            <div class="info-item" style="grid-column:1/-1">
                <div class="info-label">Téléphone</div>
                <div class="info-val">
                    ${m.tel_sur_place
                        ? `<a href="tel:${m.tel_sur_place}" style="color:var(--blue-light);font-weight:600">${m.tel_sur_place}</a>`
                        : '–'}
                </div>
            </div>
        `;

        // ── Intervention ──
        const ii = document.getElementById('interventionInfo');
        if (ii) ii.innerHTML = `
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
                       target="_blank" style="color:var(--blue-light)">
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
        const dt = document.getElementById('descriptionText');
        if (dt) dt.textContent = m.description || '–';

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
        if (!grid) return;
        grid.innerHTML = '';

        const avant = (m.photos || []).filter(p => p.type_photo === 'avant');
        const apres = (m.photos || []).filter(p => p.type_photo === 'apres');
        if (counts) counts.textContent = `${avant.length} avant · ${apres.length} après`;

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

        const btnAvant = document.getElementById('btnPhotoAvant');
        const btnApres = document.getElementById('btnPhotoApres');
        const st = m.state;
        if (btnAvant) btnAvant.style.display = ['nouveau','assigne','rdv_planifie','en_cours'].includes(st) ? 'flex' : 'none';
        if (btnApres) btnApres.style.display = ['en_cours','travaux_en_cours','devis_accepte'].includes(st) ? 'flex' : 'none';
    }

    function addPhotoThumb({ type, preview }) {
        const grid = document.getElementById('photosGrid');
        if (!grid) return;
        const thumb = document.createElement('div');
        thumb.className = `photo-thumb ${type}`;
        thumb.innerHTML = `<img src="${preview}" alt="Photo ${type}"/><div class="photo-thumb-label">${type}</div>`;
        grid.appendChild(thumb);
    }

    function refreshPhotoCounts() {
        if (!_mission) return;
        const avant = document.querySelectorAll('.photo-thumb.avant').length;
        const apres = document.querySelectorAll('.photo-thumb.apres').length;
        const el = document.getElementById('photoCounts');
        if (el) el.textContent = `${avant} avant · ${apres} après`;
    }

    /* ── Devis ── */
    function _renderDevis(m) {
        const card    = document.getElementById('devisCard');
        const content = document.getElementById('devisContent');
        const badge   = document.getElementById('devisStatusBadge');
        if (!content) return;

        const devis = m.devis || null;

        if (!devis) {
            if (badge) badge.style.display = 'none';
            const canCreate = ['en_cours','rdv_planifie','assigne'].includes(m.state);
            content.innerHTML = canCreate
                ? `<p style="color:#9CA3AF;font-size:13px;margin-bottom:12px">Aucun devis créé</p>`
                : `<p style="color:#9CA3AF;font-size:13px">–</p>`;
            return;
        }

        const devisStates = {
            brouillon: { label: 'Brouillon', color: '#6B7280', bg: '#F3F4F6' },
            envoye:    { label: 'Envoyé',    color: '#D97706', bg: '#FEF3C7' },
            accepte:   { label: '✅ Accepté', color: '#059669', bg: '#D1FAE5' },
            refuse:    { label: '❌ Refusé',  color: '#DC2626', bg: '#FEE2E2' },
        };
        const ds = devisStates[devis.state] || devisStates.brouillon;
        if (badge) {
            badge.textContent      = ds.label;
            badge.style.color      = ds.color;
            badge.style.background = ds.bg;
            badge.style.display    = 'inline-block';
            badge.style.padding    = '3px 10px';
            badge.style.borderRadius = '20px';
            badge.style.fontSize   = '12px';
            badge.style.fontWeight = '600';
        }

        const lignesHtml = (devis.lignes || []).map(l => `
            <div style="display:flex;justify-content:space-between;padding:6px 0;font-size:13px;border-bottom:1px solid #E5E7EB">
                <span>${l.description} × ${l.quantite}</span>
                <span style="font-weight:600">${_fmt(l.montant_total)} €</span>
            </div>
        `).join('');

        content.innerHTML = `
            ${lignesHtml}
            <div style="display:flex;justify-content:space-between;margin-top:12px;font-size:16px;font-weight:800;color:#1E40AF">
                <span>Total TTC</span>
                <span>${_fmt(devis.montant_total)} €</span>
            </div>
        `;
    }

    /* ── Actions workflow ── */
    function _renderActions(m) {
        const block = document.getElementById('missionActions');
        if (!block) return;
        block.innerHTML = '';

        const state = m.state;

        if (['rdv_planifie','assigne'].includes(state)) {
            block.appendChild(_btn('🔧 Démarrer l\'intervention', 'btn-start', async () => {
                const avant = document.querySelectorAll('.photo-thumb.avant').length;
                if (avant === 0) {
                    Toast.show('⚠️ Prenez des photos AVANT de démarrer', 'warning');
                    return;
                }
                await _action('DEMARRER_MISSION', () => API.demarrer(m.id), { missionId: m.id });
            }));
        }

        if (['en_cours','rdv_planifie'].includes(state) && !m.devis) {
            block.appendChild(_btn('💶 Créer un devis', 'btn-nav', () => DevisForm.open(m.id)));
        }

        if (m.devis?.state === 'brouillon') {
            block.appendChild(_btn('✏️ Modifier le devis', 'btn-nav', () => DevisForm.open(m.id, m.devis)));
        }

        if (m.devis?.state === 'envoye') {
            block.appendChild(_btn('✅ Faire signer le client', 'btn-start', () => Signature.open(m.devis.id, m.id)));
            block.appendChild(_btn('❌ Client refuse', 'btn-danger', async () => {
                if (!confirm('Confirmer le refus ?')) return;
                await _action('REFUSER_DEVIS', () => API.refuserDevis(m.devis.id), { devisId: m.devis.id });
            }));
        }

        if (['devis_accepte','travaux_en_cours','en_cours'].includes(state)) {
            block.appendChild(_btn('🎉 Terminer & clôturer', 'btn-start', async () => {
                const apres = document.querySelectorAll('.photo-thumb.apres').length;
                if (apres === 0) {
                    Toast.show('⚠️ Prenez des photos APRÈS les travaux', 'warning');
                    return;
                }
                if (!confirm('Confirmer la clôture de la mission ?')) return;
                await _action('TERMINER_MISSION', () => API.terminer(m.id), { missionId: m.id });
            }));
        }

        if (m.tel_sur_place) {
            block.appendChild(_btn(`📞 Appeler ${m.tel_sur_place}`, 'btn-call', () => {
                window.location.href = `tel:${m.tel_sur_place}`;
            }));
        }

        if (m.adresse) {
            block.appendChild(_btn('🗺 Ouvrir dans Maps', 'btn-nav', () => {
                window.open(`https://maps.google.com/?q=${encodeURIComponent(m.adresse)}`);
            }));
        }
    }

    function _btn(label, cls, onClick) {
        const btn = document.createElement('button');
        btn.className = cls;
        btn.innerHTML = `<span>${label}</span>`;
        btn.addEventListener('click', onClick);
        return btn;
    }

    async function _action(type, apiFn, queuePayload) {
        try {
            const result = await Offline.tryOrQueue(type, apiFn, queuePayload);
            if (!result?.queued) {
                Toast.show('✅ Action enregistrée', 'success');
                await MissionDetail.reload();
            }
        } catch (err) {
            Toast.show('Erreur: ' + err.message, 'error');
        }
    }

    /* ── Helpers ── */
    function _fmt(n) { return parseFloat(n || 0).toFixed(2).replace('.', ','); }
    function _formatDate(dt) {
        if (!dt) return '–';
        return new Date(dt).toLocaleDateString('fr-FR', { weekday:'short', day:'numeric', month:'short', hour:'2-digit', minute:'2-digit' });
    }
    function _sourceLabel(s) {
        return { assurance:'🏢 Assurance', particulier:'👤 Particulier', entreprise:'🏭 Entreprise' }[s] || (s || '–');
    }

    /* ── API publique ── */
    return {
        open,
        reload: async () => { await _load(); },
        getMission: () => _mission,
        addPhotoThumb,
        refreshPhotoCounts,
    };
})();
