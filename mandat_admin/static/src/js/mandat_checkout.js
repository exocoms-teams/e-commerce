/** @odoo-module **/
console.log('[mandat_admin] JS chargé ✓');

function isMandatSelected() {
    const checked = document.querySelector('input[name="o_payment_radio"]:checked');
    if (checked) {
        return checked.dataset.providerCode === 'mandat_administratif'
            || checked.dataset.paymentMethodCode === 'mandat_administratif';
    }
    // Seul mode de paiement : pas de radio, on vérifie si le champ est visible
    const siret = document.getElementById('mandat_siret');
    return !!(siret && siret.offsetParent !== null);
}

// Phase de capture : intercepte avant OWL
document.addEventListener('click', async function (e) {
    const btn = e.target.closest('.o_payment_submit_button');
    if (!btn) return;
    if (!isMandatSelected()) return;

    // On stoppe TOUJOURS dès que mandat est sélectionné — qu'il y ait erreur ou non
    e.stopImmediatePropagation();
    e.preventDefault();

    const siret = document.getElementById('mandat_siret')?.value?.trim();
    const iban = document.getElementById('mandat_iban')?.value?.trim();
    const ordonnateur = document.getElementById('mandat_ordonnateur')?.value?.trim();
    const comptable = document.getElementById('mandat_comptable')?.value?.trim();
    const errorDiv = document.getElementById('mandat_form_error');

    if (!siret || !iban || !ordonnateur || !comptable) {
        if (errorDiv) errorDiv.style.display = 'block';
        return; // stoppé — OWL ne verra jamais ce clic
    }
    if (errorDiv) errorDiv.style.display = 'none';
    btn.disabled = true;

    try {
        const resp = await fetch('/mandat/submit_payment', {
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
            window.location.assign('/payment/status');
        } else {
            btn.disabled = false;
            console.error('[mandat_admin] Erreur:', data?.result?.error);
        }
    } catch (err) {
        btn.disabled = false;
        console.error('[mandat_admin] Fetch error:', err);
    }
}, true);
