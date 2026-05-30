/**
 * devis.js — Formulaire de création et gestion des devis
 */

window.DevisForm = (() => {
    let _missionId = null;
    let _devisId   = null;
    let _lignes    = [];

    function open(missionId, existingDevis = null) {
        _missionId = missionId;
        _lignes    = [];

        if (existingDevis) {
            _devisId = existingDevis.id;
            _lignes  = existingDevis.ligne_ids?.map(l => ({
                id:           l.id,
                description:  l.description,
                quantite:     l.quantite,
                prix_unitaire:l.prix_unitaire,
                montant_total:l.montant_total,
            })) || [];
        } else {
            _devisId = null;
            // Ligne par défaut
            _lignes = [{ description: '', quantite: 1, prix_unitaire: 0, montant_total: 0 }];
        }

        App.showView('devis', 'Créer un Devis');
        renderLignes();
        updateTotaux();
    }

    function renderLignes() {
        const container = document.getElementById('devisLignes');
        container.innerHTML = '';

        _lignes.forEach((ligne, idx) => {
            const div = document.createElement('div');
            div.className = 'devis-ligne';
            div.innerHTML = `
                <input class="field-input" type="text" placeholder="Description"
                       value="${_escape(ligne.description)}"
                       oninput="DevisForm.updateLigne(${idx}, 'description', this.value)"/>
                <input class="field-input" type="number" min="0.01" step="0.01" placeholder="Qté"
                       value="${ligne.quantite}"
                       oninput="DevisForm.updateLigne(${idx}, 'quantite', parseFloat(this.value)||0)"/>
                <input class="field-input" type="number" min="0" step="0.01" placeholder="Prix HT"
                       value="${ligne.prix_unitaire}"
                       oninput="DevisForm.updateLigne(${idx}, 'prix_unitaire', parseFloat(this.value)||0)"/>
                <button class="btn btn-danger btn-sm" style="padding:8px 10px; min-width:32px"
                        onclick="DevisForm.removeLigne(${idx})">✕</button>
            `;
            container.appendChild(div);
        });
    }

    function _escape(str) {
        return String(str).replace(/"/g, '&quot;');
    }

    function updateLigne(idx, field, value) {
        _lignes[idx][field] = value;
        _lignes[idx].montant_total = _lignes[idx].quantite * _lignes[idx].prix_unitaire;
        updateTotaux();
    }

    function updateTotaux() {
        const ht  = _lignes.reduce((sum, l) => sum + (l.montant_total || 0), 0);
        const tva = ht * 0.2;
        const ttc = ht + tva;

        document.getElementById('totalHT').textContent  = _fmt(ht);
        document.getElementById('totalTVA').textContent = _fmt(tva);
        document.getElementById('totalTTC').textContent = _fmt(ttc);
    }

    function _fmt(n) {
        return n.toFixed(2).replace('.', ',') + ' €';
    }

    return {
        open,
        updateLigne,

        addLigne() {
            _lignes.push({ description: '', quantite: 1, prix_unitaire: 0, montant_total: 0 });
            renderLignes();
            updateTotaux();
        },

        removeLigne(idx) {
            if (_lignes.length <= 1) {
                Toast.show('Minimum 1 ligne requise', 'warning');
                return;
            }
            _lignes.splice(idx, 1);
            renderLignes();
            updateTotaux();
        },

        _validate() {
            if (!_lignes.length) {
                Toast.show('Ajoutez au moins une ligne', 'warning');
                return false;
            }
            for (const [i, l] of _lignes.entries()) {
                if (!l.description.trim()) {
                    Toast.show(`Ligne ${i+1} : description manquante`, 'warning');
                    return false;
                }
                if (l.prix_unitaire <= 0) {
                    Toast.show(`Ligne ${i+1} : prix invalide`, 'warning');
                    return false;
                }
            }
            return true;
        },

        _buildPayload() {
            const note = document.getElementById('devisNote')?.value.trim() || '';
            return {
                ligne_ids: _lignes.map(l => ({
                    description:   l.description.trim(),
                    quantite:      parseFloat(l.quantite) || 1,
                    prix_unitaire: parseFloat(l.prix_unitaire) || 0,
                })),
                note_client: note,
                tva: 20.0,
            };
        },

        async save() {
            if (!this._validate()) return;
            const payload = this._buildPayload();

            try {
                const result = await Offline.tryOrQueue(
                    'CREATE_DEVIS',
                    () => API.createDevis(_missionId, payload),
                    { missionId: _missionId, payload }
                );
                if (result && !result.queued) {
                    _devisId = result.devis_id || result.id;
                    Toast.show('💾 Devis enregistré', 'success');
                    const btnEnv = document.getElementById('btnEnvoyerDevis');
                    if (btnEnv) btnEnv.style.display = 'flex';
                    // Retourner sur la mission pour voir le devis
                    setTimeout(() => {
                        if (window.MissionDetail) MissionDetail.reload();
                    }, 500);
                }
            } catch (err) {
                Toast.show('Erreur: ' + err.message, 'error');
            }
        },

        async envoyer() {
            if (!this._validate()) return;

            // Si pas encore sauvegardé → sauvegarder d'abord
            if (!_devisId) {
                await this.save();
                if (!_devisId) return;
            }

            try {
                await Offline.tryOrQueue(
                    'ENVOYER_DEVIS',
                    () => API.envoyerDevis(_devisId),
                    { devisId: _devisId }
                );
                Toast.show('📤 Devis envoyé au client', 'success');
                App.showView('mission', 'Mission');
                MissionDetail.reload();
            } catch (err) {
                Toast.show('Erreur: ' + err.message, 'error');
            }
        },
    };
})();
