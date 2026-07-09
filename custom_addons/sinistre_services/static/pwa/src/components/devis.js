/**
 * devis.js — Formulaire de création ET modification du devis
 *
 * Règles métier :
 *  - Création : états 'en_cours', 'rdv_planifie', 'assigne'
 *  - Modification (avenant) : possible si devis déjà accepté PENDANT l'intervention
 *    → déclenche une re-signature obligatoire du client
 *  - Après enregistrement/envoi : retour mission
 */

window.DevisForm = (() => {
    let _missionId  = null;
    let _devisId    = null;
    let _lignes     = [];
    let _isAmendment = false;   // true = modification en cours d'intervention

    let _tvaRate = 20;

    function _getTvaRate() {
        const sel = document.getElementById('devisTvaSelect');
        return sel ? parseFloat(sel.value) : _tvaRate;
    }

    function onTvaChange() {
        _tvaRate = _getTvaRate();
        updateTotaux();
    }

    /* ── Ouvrir le formulaire ── */
    function open(missionId, existingDevis = null, isAmendment = false) {
        _missionId   = missionId;
        _devisId     = null;
        _lignes      = [];
        _isAmendment = isAmendment;

        if (existingDevis) {
            _devisId = existingDevis.id;
            _lignes  = (existingDevis.lignes || existingDevis.ligne_ids || []).map(l => ({
                id:            l.id,
                description:   l.description,
                quantite:      l.quantite,
                prix_unitaire: l.prix_unitaire,
                montant_total: l.montant_total,
            }));
        } else {
            _lignes = [{ description: '', quantite: 1, prix_unitaire: 0, montant_total: 0 }];
        }

        const title = isAmendment
            ? '⚠️ Modifier le Devis (Avenant)'
            : (existingDevis ? 'Modifier le Devis' : 'Créer un Devis');
        App.showView('devis', title);

        // Afficher bannière avertissement si avenant
        const banner = document.getElementById('devisAmendmentBanner');
        if (banner) {
            banner.style.display = isAmendment ? 'block' : 'none';
        }

        const actionsNormal = document.getElementById('devisActionsNormal');
        const actionsAmendment = document.getElementById('devisActionsAmendment');
        if (actionsNormal) actionsNormal.style.display = isAmendment ? 'none' : 'block';
        if (actionsAmendment) actionsAmendment.style.display = isAmendment ? 'block' : 'none';

        const noteEl = document.getElementById('devisNote');
        if (noteEl) {
            noteEl.value = existingDevis ? (existingDevis.note_client || '') : '';
        }

        const tvaSel = document.getElementById('devisTvaSelect');
        if (tvaSel) {
            const tvaVal = existingDevis
                ? String(existingDevis.tva_selection || Math.round(existingDevis.tva || 20))
                : '20';
            tvaSel.value = ['10', '20', '0'].includes(tvaVal) ? tvaVal : '20';
            _tvaRate = parseFloat(tvaSel.value);
        }

        const btnEnv = document.getElementById('btnEnvoyerDevis');
        if (btnEnv) {
            const canSend = existingDevis && !isAmendment
                && ['brouillon', 'en_revision'].includes(existingDevis.state);
            btnEnv.style.display = canSend ? 'flex' : 'none';
        }

        renderLignes();
        updateTotaux();
    }

    /* ── Rendu lignes ── */
    function renderLignes() {
        const container = document.getElementById('devisLignes');
        if (!container) return;
        container.innerHTML = '';
        _lignes.forEach((ligne, idx) => {
            const div = document.createElement('div');
            div.className = 'devis-ligne';
            div.innerHTML = `
                <input class="field-input" type="text" placeholder="Description"
                       value="${_escape(ligne.description)}"
                       oninput="DevisForm.updateLigne(${idx}, 'description', this.value)"/>
                <div style="display:flex;gap:8px">
                    <input class="field-input" type="number" min="0.01" step="0.01" placeholder="Qté"
                           value="${ligne.quantite}" style="flex:1"
                           oninput="DevisForm.updateLigne(${idx}, 'quantite', parseFloat(this.value)||0)"/>
                    <input class="field-input" type="number" min="0" step="0.01" placeholder="Prix HT"
                           value="${ligne.prix_unitaire}" style="flex:2"
                           oninput="DevisForm.updateLigne(${idx}, 'prix_unitaire', parseFloat(this.value)||0)"/>
                    <span style="line-height:44px;font-size:13px;color:#6B7280;min-width:60px;text-align:right">
                        ${_fmt(ligne.montant_total)}
                    </span>
                    <button class="btn btn-danger btn-sm" style="padding:8px 10px;min-width:32px"
                            onclick="DevisForm.removeLigne(${idx})">✕</button>
                </div>
            `;
            container.appendChild(div);
        });
    }

    function _escape(str) { return String(str).replace(/"/g, '&quot;'); }

    function updateLigne(idx, field, value) {
        _lignes[idx][field] = value;
        _lignes[idx].montant_total = _lignes[idx].quantite * _lignes[idx].prix_unitaire;
        updateTotaux();
        // Mise à jour montant ligne affichée
        renderLignes();
    }

    function updateTotaux() {
        const ht  = _lignes.reduce((sum, l) => sum + (l.montant_total || 0), 0);
        const rate = _getTvaRate();
        const tva = ht * (rate / 100);
        const ttc = ht + tva;
        const el  = (id) => document.getElementById(id);
        if (el('totalHT'))  el('totalHT').textContent  = _fmt(ht);
        if (el('totalTVA')) el('totalTVA').textContent = _fmt(tva);
        if (el('totalTTC')) el('totalTTC').textContent = _fmt(ttc);
        const lbl = document.getElementById('tvaLabel');
        if (lbl) lbl.textContent = rate === 0 ? 'Hors taxe' : `TVA (${rate}%)`;
    }

    function _fmt(n) { return parseFloat(n || 0).toFixed(2).replace('.', ',') + ' €'; }

    function _validate() {
        if (!_lignes.length) { Toast.show('Ajoutez au moins une ligne', 'warning'); return false; }
        for (const [i, l] of _lignes.entries()) {
            if (!l.description.trim()) { Toast.show(`Ligne ${i+1} : description manquante`, 'warning'); return false; }
            if ((l.quantite || 0) <= 0)   { Toast.show(`Ligne ${i+1} : quantité invalide`, 'warning'); return false; }
            if (l.prix_unitaire <= 0)  { Toast.show(`Ligne ${i+1} : prix invalide`, 'warning'); return false; }
        }
        return true;
    }

    function _buildPayload() {
        const rate = _getTvaRate();
        return {
            ligne_ids: _lignes.map(l => ({
                id:            l.id || null,
                description:   l.description.trim(),
                quantite:      parseFloat(l.quantite)      || 1,
                prix_unitaire: parseFloat(l.prix_unitaire) || 0,
            })),
            note_client:    document.getElementById('devisNote')?.value.trim() || '',
            tva:            rate,
            tva_selection:  String(Math.round(rate)),
            is_amendment:   _isAmendment,
        };
    }

    return {
        open,
        updateLigne,
        onTvaChange,

        addLigne() {
            _lignes.push({ description: '', quantite: 1, prix_unitaire: 0, montant_total: 0 });
            renderLignes();
            updateTotaux();
        },

        removeLigne(idx) {
            if (_lignes.length <= 1) { Toast.show('Minimum 1 ligne requise', 'warning'); return; }
            _lignes.splice(idx, 1);
            renderLignes();
            updateTotaux();
        },

        /* ── Enregistrer (brouillon) ── */
        async save() {
            if (!_validate()) return;
            const payload = _buildPayload();
            try {
                const result = await Offline.tryOrQueue(
                    _devisId ? 'UPDATE_DEVIS' : 'CREATE_DEVIS',
                    () => _devisId
                        ? API.updateDevis(_devisId, payload)
                        : API.createDevis(_missionId, payload),
                    { missionId: _missionId, devisId: _devisId, payload }
                );
                if (result && !result.queued) {
                    _devisId = result.devis_id || result.id || _devisId;
                    Toast.show('💾 Devis enregistré', 'success');
                    const btnEnv = document.getElementById('btnEnvoyerDevis');
                    if (btnEnv) btnEnv.style.display = 'flex';
                    setTimeout(() => MissionDetail?.reload(), 500);
                }
            } catch (err) { Toast.show('Erreur: ' + err.message, 'error'); }
        },

        /* ── Envoyer (état → envoye) ── */
        async envoyer() {
            if (!_validate()) return;
            if (!_devisId) { await this.save(); if (!_devisId) return; }
            try {
                await Offline.tryOrQueue(
                    'ENVOYER_DEVIS',
                    () => API.envoyerDevis(_devisId),
                    { devisId: _devisId }
                );
                Toast.show('📤 Devis envoyé au client', 'success');
                App.showView('mission', 'Mission');
                MissionDetail.reload();
            } catch (err) { Toast.show('Erreur: ' + err.message, 'error'); }
        },

        /* ── Sauvegarder avenant + demander re-signature ── */
        async saveAmendment() {
            if (!_validate()) return;
            const payload = _buildPayload();
            try {
                const result = await Offline.tryOrQueue(
                    'UPDATE_DEVIS',
                    () => API.updateDevis(_devisId, payload),
                    { devisId: _devisId, payload }
                );
                if (result && !result.queued) {
                    Toast.show('💾 Avenant enregistré — re-signature requise', 'warning');
                    // Ouvrir la signature en mode re-signature
                    Signature.open({ mode: 'devis_modifie', devisId: _devisId, missionId: _missionId });
                }
            } catch (err) { Toast.show('Erreur: ' + err.message, 'error'); }
        },
    };
})();

/**
 * ImportDoc — Import devis / facture depuis logiciel externe
 */
window.ImportDoc = (() => {
    let _missionId = null;
    let _type = 'devis';
    let _fileB64 = null;
    let _fileName = '';

    function open(missionId, type = 'devis') {
        _missionId = missionId;
        _type = type;
        _fileB64 = null;
        _fileName = '';
        const modal = document.getElementById('importDocModal');
        if (!modal) return;
        modal.style.display = 'flex';
        const title = document.getElementById('importDocTitle');
        if (title) title.textContent = type === 'facture' ? 'Importer une facture' : 'Importer un devis';
        const ref = document.getElementById('importDocRef');
        const ht = document.getElementById('importDocMontant');
        const fileLabel = document.getElementById('importDocFileLabel');
        const fileInput = document.getElementById('importDocFile');
        if (ref) ref.value = '';
        if (ht) ht.value = '';
        if (fileLabel) fileLabel.textContent = 'PDF ou image (max 5 Mo)';
        if (fileInput) fileInput.value = '';
    }

    function close() {
        const modal = document.getElementById('importDocModal');
        if (modal) modal.style.display = 'none';
    }

    async function onFileSelected(input) {
        const file = input.files && input.files[0];
        if (!file) return;
        const ok = ['application/pdf', 'image/jpeg', 'image/png', 'image/webp'].includes(file.type)
            || /\.(pdf|jpe?g|png|webp)$/i.test(file.name);
        if (!ok) {
            Toast.show('Format accepté : PDF, JPEG, PNG, WebP', 'warning');
            input.value = '';
            return;
        }
        if (file.size > 5 * 1024 * 1024) {
            Toast.show('Fichier trop volumineux (max 5 Mo)', 'warning');
            input.value = '';
            return;
        }
        _fileName = file.name;
        const label = document.getElementById('importDocFileLabel');
        if (label) label.textContent = file.name;
        const reader = new FileReader();
        reader.onload = (e) => {
            const dataUrl = e.target.result;
            _fileB64 = String(dataUrl).split(',')[1] || '';
        };
        reader.readAsDataURL(file);
    }

    async function submit() {
        const ref = (document.getElementById('importDocRef')?.value || '').trim();
        const montant = parseFloat(document.getElementById('importDocMontant')?.value || '0');
        if (!ref) { Toast.show('Référence requise', 'warning'); return; }
        if (!montant || montant <= 0) { Toast.show('Montant HT invalide', 'warning'); return; }
        if (!_missionId) return;
        try {
            await API.importDocument(_missionId, {
                type: _type,
                reference_externe: ref,
                montant_ht: montant,
                fichier: _fileB64 || '',
                fichier_name: _fileName || `${ref}.pdf`,
            });
            Toast.show(_type === 'facture' ? 'Facture importée' : 'Devis importé', 'success');
            close();
            if (window.MissionDetail) await MissionDetail.reload();
        } catch (err) {
            Toast.show('Erreur : ' + err.message, 'error');
        }
    }

    return { open, close, onFileSelected, submit };
})();
