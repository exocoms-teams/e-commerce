/**
 * mission_detail.js — Écran de détail d'une mission
 */

window.MissionDetail = (() => {
    let _mission   = null;
    let _missionId = null;
    let _isLoading = false;

    async function open(idOrRef) {
        _missionId = (typeof idOrRef === 'string' && /^\d+$/.test(idOrRef)) ? parseInt(idOrRef) : idOrRef;
        App.showView('mission');
        await _load();
    }

    async function _load() {
        if (_isLoading) return;
        _isLoading = true;
        const banner = document.getElementById('missionBanner');
        if (banner) banner.textContent = 'Chargement…';
        try {
            const data = await API.getMission(_missionId);
            _mission   = data.mission || data;
        } catch (err) {
            Toast.show('Impossible de charger la mission', 'error');
            App.goBack();
            _isLoading = false;
            return;
        } finally { _isLoading = false; }
        Photos.setMission(_mission.id);
        _render();
    }

    function _render() {
        if (!_mission) return;
        const m = _mission;

        const titleEl = document.getElementById('topbarTitle');
        if (titleEl) titleEl.textContent = m.reference || 'Mission';

        const state   = CONFIG.STATE_LABELS[m.state] || { label: m.state, icon: '❓' };
        const urgConf = CONFIG.URGENCE_COLORS[m.urgence] || CONFIG.URGENCE_COLORS.normale;
        const banner  = document.getElementById('missionBanner');
        if (banner) { banner.style.background = urgConf.bg; banner.style.color = urgConf.text; }
        const bi = document.getElementById('missionBannerIcon');
        const bt = document.getElementById('missionBannerText');
        if (bi) bi.textContent = state.icon;
        if (bt) bt.textContent = state.label;

        _renderClient(m, urgConf);
        _renderIntervention(m, urgConf);
        _renderDescription(m);
        _renderPhotos(m);
        _renderDevis(m);
        _renderNotes(m);
        _renderActions(m);
        _renderMessagerieBadge(m);
    }

    function _renderClient(m, urgConf) {
        const ci = document.getElementById('clientInfo');
        if (!ci) return;
        ci.innerHTML = `
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
    }

    function _renderIntervention(m, urgConf) {
        const ii = document.getElementById('interventionInfo');
        if (!ii) return;
        ii.innerHTML = `
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
                       target="_blank" style="color:var(--blue-light)">📍 ${m.adresse || '–'}</a>
                </div>
            </div>
            ${m.date_rdv ? `<div class="info-item"><div class="info-label">Date RDV</div><div class="info-val">${_formatDate(m.date_rdv)}</div></div>` : ''}
            ${m.montant_devis ? `
            <div class="info-item">
                <div class="info-label">Montant Devis</div>
                <div class="info-val" style="font-weight:700;color:var(--blue)">${_fmt(m.montant_devis)} €</div>
            </div>
            <div class="info-item">
                <div class="info-label">Reste à charge</div>
                <div class="info-val" style="font-weight:700">${_fmt(m.reste_a_charge)} €</div>
            </div>` : ''}
            ${m.signature_avant ? `
            <div class="info-item" style="grid-column:1/-1">
                <div class="info-label">✅ Signature avant</div>
                <div class="info-val" style="color:#059669">Enregistrée</div>
            </div>` : ''}
            ${m.signature_apres ? `
            <div class="info-item" style="grid-column:1/-1">
                <div class="info-label">✅ Signature après</div>
                <div class="info-val" style="color:#059669">Enregistrée — facture générée</div>
            </div>` : ''}
        `;
    }

    function _renderDescription(m) {
        const dt = document.getElementById('descriptionText');
        if (dt) dt.textContent = m.description || '–';
    }

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
                <img src="${photo.url || '#'}" alt="Photo ${photo.type_photo}" onerror="this.style.display='none'"/>
                <div class="photo-thumb-label">${photo.type_photo}</div>
            `;
            grid.appendChild(thumb);
        });
        const st = m.state;
        const btnAvant = document.getElementById('btnPhotoAvant');
        const btnApres = document.getElementById('btnPhotoApres');
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
        const el    = document.getElementById('photoCounts');
        if (el) el.textContent = `${avant} avant · ${apres} après`;
    }

    function _renderDevis(m) {
        const content = document.getElementById('devisContent');
        const badge   = document.getElementById('devisStatusBadge');
        if (!content) return;
        const devis = m.devis || null;
        if (!devis) {
            if (badge) badge.style.display = 'none';
            content.innerHTML = ['en_cours','rdv_planifie','assigne','nouveau'].includes(m.state)
                ? `<p style="color:#9CA3AF;font-size:13px;margin-bottom:12px">Aucun devis créé</p>`
                : `<p style="color:#9CA3AF;font-size:13px">–</p>`;
            return;
        }
        const devisStates = {
            brouillon:   { label: 'Brouillon',      color: '#6B7280', bg: '#F3F4F6' },
            envoye:      { label: 'Envoyé',          color: '#D97706', bg: '#FEF3C7' },
            accepte:     { label: '✅ Accepté',      color: '#059669', bg: '#D1FAE5' },
            refuse:      { label: '❌ Refusé',       color: '#DC2626', bg: '#FEE2E2' },
            en_revision: { label: '⚠️ En révision',  color: '#7C3AED', bg: '#EDE9FE' },
        };
        const ds = devisStates[devis.state] || devisStates.brouillon;
        if (badge) {
            Object.assign(badge.style, { display:'inline-block', padding:'3px 10px', borderRadius:'20px', fontSize:'12px', fontWeight:'600', color:ds.color, background:ds.bg });
            badge.textContent = ds.label;
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
                <span>Total TTC</span><span>${_fmt(devis.montant_total)} €</span>
            </div>
            ${devis.note_client ? `<p style="margin-top:8px;font-size:12px;color:#6B7280;font-style:italic">${devis.note_client}</p>` : ''}
        `;
    }

    function _renderNotes(m) {
        const textarea = document.getElementById('missionNotesText');
        if (textarea && m.notes_artisan !== undefined) textarea.value = m.notes_artisan || '';
    }

    function _renderMessagerieBadge(m) {
        const badge = document.getElementById('msgBadge');
        const count = m.messages_non_lus || 0;
        if (badge) { badge.textContent = count || ''; badge.style.display = count ? 'flex' : 'none'; }
    }

    /* ══════════════════════════════════════════════════════════
       ACTIONS — Workflow complet
    ══════════════════════════════════════════════════════════ */
    function _renderActions(m) {
        const block = document.getElementById('missionActions');
        if (!block) return;
        block.innerHTML = '';

        const st  = m.state;
        const dev = m.devis;

        // États où l'intervention peut commencer ou est en cours
        const isActive = ['nouveau','assigne','rdv_planifie','en_cours','devis_accepte','travaux_en_cours','devis_envoye','devis_refuse'].includes(st);
        // États avant démarrage
        const isPreStart = ['nouveau','assigne','rdv_planifie'].includes(st);
        // États après démarrage
        const isStarted = ['en_cours','devis_accepte','travaux_en_cours','devis_envoye','devis_refuse'].includes(st);

        /* ── 1. Signature AVANT (si pas encore faite et mission pas terminée) ── */
        if (!m.signature_avant && isActive) {
            block.appendChild(_btn('✍️ Signature Avant Intervention', 'btn-start', () =>
                Signature.open({ mode: 'avant', missionId: m.id })
            ));
        }

        /* ── 2. Démarrer (si signature avant OK — états larges) ── */
        if (isPreStart || (isActive && !isStarted)) {
            block.appendChild(_btn('🔧 Démarrer l\'intervention', 'btn-start', async () => {
                if (!m.signature_avant) {
                    Toast.show('⚠️ La signature AVANT est obligatoire', 'warning');
                    return;
                }
                const avant = document.querySelectorAll('.photo-thumb.avant').length;
                if (avant === 0) {
                    Toast.show('⚠️ Prenez des photos AVANT de démarrer', 'warning');
                    return;
                }
                await _action('DEMARRER_MISSION', () => API.demarrer(m.id), { missionId: m.id });
            }));
        }

        /* ── 3. Créer un devis ── */
        if (isActive && !dev) {
            block.appendChild(_btn('💶 Créer un devis', 'btn-nav', () => DevisForm.open(m.id)));
        }

        /* ── 4a. Modifier devis brouillon ── */
        if (dev?.state === 'brouillon') {
            block.appendChild(_btn('✏️ Modifier le devis', 'btn-nav', () => DevisForm.open(m.id, dev, false)));
        }

        /* ── 4b. Avenant (devis accepté pendant travaux) ── */
        if (dev?.state === 'accepte' && isStarted) {
            block.appendChild(_btn('⚠️ Modifier le devis (avenant)', 'btn-warning', () => {
                if (!confirm('Modifier le devis obligera le client à signer à nouveau. Continuer ?')) return;
                DevisForm.open(m.id, dev, true);
            }));
        }

        /* ── 4c. Faire signer devis envoyé ── */
        if (dev?.state === 'envoye') {
            block.appendChild(_btn('✅ Faire signer le client (devis)', 'btn-start', () =>
                Signature.open({ mode: 'devis', devisId: dev.id, missionId: m.id })
            ));
            block.appendChild(_btn('❌ Client refuse le devis', 'btn-danger', async () => {
                if (!confirm('Confirmer le refus ?')) return;
                await _action('REFUSER_DEVIS', () => API.refuserDevis(dev.id), { devisId: dev.id });
            }));
        }

        /* ── 4d. Re-signature devis en révision ── */
        if (dev?.state === 'en_revision') {
            block.appendChild(_btn('✍️ Re-signature client (devis modifié)', 'btn-warning', () =>
                Signature.open({ mode: 'devis_modifie', devisId: dev.id, missionId: m.id })
            ));
        }

        /* ── 5. Signature APRÈS + Clôture ── */
        if (isStarted) {
            const apres = document.querySelectorAll('.photo-thumb.apres').length;
            if (!m.signature_apres) {
                block.appendChild(_btn('✍️ Signature Après Intervention', 'btn-start', async () => {
                    if (apres === 0) {
                        Toast.show('⚠️ Prenez des photos APRÈS les travaux avant de faire signer', 'warning');
                        return;
                    }
                    Signature.open({ mode: 'apres', missionId: m.id });
                }));
            } else {
                block.appendChild(_btn('🎉 Clôturer la mission', 'btn-start', async () => {
                    if (apres === 0) {
                        Toast.show('⚠️ Prenez des photos APRÈS les travaux', 'warning');
                        return;
                    }
                    if (!confirm('Confirmer la clôture de la mission ?')) return;
                    await _action('TERMINER_MISSION', () => API.terminer(m.id), { missionId: m.id });
                }));
            }
        }

        /* ── 6. Contact / Maps ── */
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
        } catch (err) { Toast.show('Erreur: ' + err.message, 'error'); }
    }

    async function saveNotes() {
        const textarea = document.getElementById('missionNotesText');
        if (!textarea || !_missionId) return;
        try {
            await API.saveNotes(_missionId, textarea.value.trim());
            Toast.show('📝 Notes enregistrées', 'success');
        } catch (err) { Toast.show('Erreur notes: ' + err.message, 'error'); }
    }

    function _fmt(n) { return parseFloat(n || 0).toFixed(2).replace('.', ','); }
    function _formatDate(dt) {
        if (!dt) return '–';
        return new Date(dt).toLocaleDateString('fr-FR', { weekday:'short', day:'numeric', month:'short', hour:'2-digit', minute:'2-digit' });
    }
    function _sourceLabel(s) {
        return { assurance:'🏢 Assurance', particulier:'👤 Particulier', entreprise:'🏭 Entreprise' }[s] || (s || '–');
    }

    return {
        open,
        reload: async () => { await _load(); },
        getMission: () => _mission,
        addPhotoThumb,
        refreshPhotoCounts,
        saveNotes,
        openMessagerie: () => { if (_missionId) Messagerie.open(_missionId); },
    };
})();
