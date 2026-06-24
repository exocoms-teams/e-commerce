/** @odoo-module **/
console.log('[mandat_admin] JS chargé ✓');

function isMandatSelected() {
    const checked = document.querySelector('input[name="o_payment_radio"]:checked');
    if (checked) {
        return checked.dataset.providerCode === 'mandat_administratif'
            || checked.dataset.paymentMethodCode === 'mandat_administratif';
    }
    // Seul mode de paiement, pas de radio — on vérifie si le champ SIRET est présent
    return !!document.getElementById('mandat_siret');
}

async function handleMandatPayment(e) {
    // On cible uniquement le bouton Pay Now de la page paiement
    const btn = e.target.closest('.o_payment_submit_button');
    if (!btn) return;
    if (!isMandatSelected()) return;

    e.preventDefault();
    e.stopPropagation();

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
            window.location.assign('/shop/confirmation');
        } else {
            console.error('[mandat_admin] Erreur:', data?.result?.error);
            btn.disabled = false;
        }
    } catch (err) {
        console.error('[mandat_admin] Fetch error:', err);
        btn.disabled = false;
    }
}

// Phase de capture : on intercepte avant qu'OWL ne traite le clic
document.addEventListener('click', handleMandatPayment, true);
