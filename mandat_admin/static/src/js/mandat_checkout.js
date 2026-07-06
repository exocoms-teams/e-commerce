/** @odoo-module **/
console.log('[mandat_admin] JS chargé ✓');

// Délégation d'événement : fonctionne même si le bouton est rendu après le chargement
document.addEventListener('click', async function (e) {
    const btn = e.target.closest('#mandat_confirm_btn');
    if (!btn) return;

    e.preventDefault();
    e.stopImmediatePropagation();

    const siret = document.getElementById('mandat_siret')?.value?.trim();
    const ordonnateur = document.getElementById('mandat_ordonnateur')?.value?.trim();
    const comptable = document.getElementById('mandat_comptable')?.value?.trim();
    const errorDiv = document.getElementById('mandat_form_error');

    if (!siret || !ordonnateur || !comptable) {
        if (errorDiv) errorDiv.style.display = 'block';
        return;
    }
    if (errorDiv) errorDiv.style.display = 'none';

    btn.disabled = true;
    btn.textContent = 'Traitement en cours...';

    try {
        const resp = await fetch('/mandat/submit', {
            method: 'POST',
            headers: { 'Content-Type': 'application/json' },
            body: JSON.stringify({
                jsonrpc: '2.0', method: 'call', id: 1,
                params: {
                    siret, ordonnateur, comptable,
                    qualite: document.getElementById('mandat_qualite')?.value?.trim() || '',
                    ej: document.getElementById('mandat_ej')?.value?.trim() || '',
                    service: document.getElementById('mandat_service')?.value?.trim() || '',
                    reference: document.getElementById('mandat_reference')?.value?.trim() || '',
                    service_chorus: document.getElementById('mandat_service_chorus')?.value?.trim() || '',
                    code_tiers_chorus: document.getElementById('mandat_code_tiers_chorus')?.value?.trim() || '',
                },
            }),
        });
        const data = await resp.json();
        console.log('[mandat_admin] réponse serveur:', JSON.stringify(data));
        if (data?.result?.success) {
            window.location.assign(data.result.redirect || '/shop/confirmation');
        } else {
            const msg = data?.result?.error || data?.error?.data?.message || data?.error?.message || 'Erreur inconnue';
            console.error('[mandat_admin] Erreur:', msg);
            if (errorDiv) {
                errorDiv.textContent = msg;
                errorDiv.style.display = 'block';
            }
            btn.disabled = false;
            btn.textContent = '🏛 Confirmer le paiement par Mandat Administratif';
        }
    } catch (err) {
        console.error('[mandat_admin] Fetch error:', err);
        btn.disabled = false;
        btn.textContent = '🏛 Confirmer le paiement par Mandat Administratif';
    }
});
