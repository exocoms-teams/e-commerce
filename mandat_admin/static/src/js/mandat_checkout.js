/** @odoo-module **/
console.log('[mandat_admin] JS chargé ✓');

function isMandatSelected() {
    const checked = document.querySelector('input[name="o_payment_radio"]:checked');
    if (checked) {
        return checked.dataset.providerCode === 'mandat_administratif'
            || checked.dataset.paymentMethodCode === 'mandat_administratif';
    }
    const siret = document.getElementById('mandat_siret');
    return !!(siret && siret.offsetParent !== null);
}

// Quand true, le prochain clic est laissé passer à OWL sans interception
let _dataAlreadySaved = false;

document.addEventListener('click', async function (e) {
    const btn = e.target.closest('.o_payment_submit_button');
    if (!btn || !isMandatSelected()) return;

    // Deuxième clic (après sauvegarde) : on laisse OWL gérer
    if (_dataAlreadySaved) {
        _dataAlreadySaved = false;
        return;
    }

    // On stoppe toujours avant de valider
    e.stopImmediatePropagation();
    e.preventDefault();

    const siret = document.getElementById('mandat_siret')?.value?.trim();
    const iban = document.getElementById('mandat_iban')?.value?.trim();
    const ordonnateur = document.getElementById('mandat_ordonnateur')?.value?.trim();
    const comptable = document.getElementById('mandat_comptable')?.value?.trim();
    const errorDiv = document.getElementById('mandat_form_error');

    if (!siret || !iban || !ordonnateur || !comptable) {
        if (errorDiv) errorDiv.style.display = 'block';
        return;
    }
    if (errorDiv) errorDiv.style.display = 'none';
    btn.disabled = true;

    try {
        const resp = await fetch('/mandat/save_checkout_data', {
            method: 'POST',
            headers: { 'Content-Type': 'application/json' },
            body: JSON.stringify({
                jsonrpc: '2.0', method: 'call', id: 1,
                params: {
                    siret, iban, ordonnateur, comptable,
                    qualite: document.getElementById('mandat_qualite')?.value?.trim() || '',
                    ej: document.getElementById('mandat_ej')?.value?.trim() || '',
                    service: document.getElementById('mandat_service')?.value?.trim() || '',
                    reference: document.getElementById('mandat_reference')?.value?.trim() || '',
                },
            }),
        });
        const data = await resp.json();
        if (data?.result?.success) {
            // Données sauvegardées — on laisse OWL créer la transaction et faire le redirect
            _dataAlreadySaved = true;
            btn.disabled = false;
            btn.dispatchEvent(new MouseEvent('click', { bubbles: true, cancelable: true }));
        } else {
            btn.disabled = false;
            console.error('[mandat_admin] Erreur save:', data?.result?.error);
        }
    } catch (err) {
        btn.disabled = false;
        console.error('[mandat_admin] Fetch error:', err);
    }
}, true);
