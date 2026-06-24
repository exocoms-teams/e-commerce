/** @odoo-module **/
import { PaymentForm } from '@payment/js/payment_form';
import { patch } from '@web/core/utils/patch';
import { onMounted } from '@odoo/owl';

console.log('[mandat_admin] module JS chargé ✓');

function isMandatSelected() {
    // Si un radio est coché, on vérifie son provider code
    const checkedRadio = document.querySelector('input[name="o_payment_radio"]:checked');
    if (checkedRadio) {
        return checkedRadio.dataset.providerCode === 'mandat_administratif'
            || checkedRadio.dataset.paymentMethodCode === 'mandat_administratif';
    }
    // Pas de radio (un seul mode de paiement) → on vérifie si notre form existe dans le DOM
    return !!document.getElementById('mandat_administratif_form');
}

function updateMandatVisibility() {
    const active = isMandatSelected();
    console.log('[mandat_admin] updateMandatVisibility, active:', active);
    document.body.classList.toggle('o_mandat_active', active);
}

patch(PaymentForm.prototype, {

    setup() {
        super.setup(...arguments);
        onMounted(() => updateMandatVisibility());
    },

    async _updateSelectedPaymentOption() {
        await super._updateSelectedPaymentOption(...arguments);
        updateMandatVisibility();
    },

    // Intercepte le redirect flow AVANT qu'il cherche #o_payment_redirect_form
    async _processRedirectFlow(providerCode, paymentOptionId, redirectUrl, processingValues) {
        if (providerCode === 'mandat_administratif') {
            console.log('[mandat_admin] _processRedirectFlow intercepté → /payment/status');
            window.location.assign('/payment/status');
            return;
        }
        return super._processRedirectFlow(...arguments);
    },

    async submitForm(...args) {
        console.log('[mandat_admin] submitForm appelé, isMandatSelected:', isMandatSelected());
        if (!isMandatSelected()) {
            return super.submitForm(...args);
        }

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

        try {
            const resp = await fetch('/mandat/submit_payment', {
                method: 'POST',
                headers: { 'Content-Type': 'application/json' },
                body: JSON.stringify({
                    jsonrpc: '2.0', method: 'call', id: 1,
                    params: {
                        siret, iban, ordonnateur,
                        qualite: document.getElementById('mandat_qualite')?.value?.trim() || '',
                        comptable,
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
                console.error('[mandat_admin] Erreur serveur:', data?.result?.error);
            }
        } catch (e) {
            console.error('[mandat_admin] Erreur paiement:', e);
        }
    },
});
