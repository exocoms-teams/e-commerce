/** @odoo-module **/
import { PaymentForm } from '@payment/js/payment_form';
import { patch } from '@web/core/utils/patch';

async function saveMandatData() {
    const params = {
        siret: document.getElementById('mandat_siret')?.value?.trim() || '',
        iban: document.getElementById('mandat_iban')?.value?.trim() || '',
        ordonnateur: document.getElementById('mandat_ordonnateur')?.value?.trim() || '',
        qualite: document.getElementById('mandat_qualite')?.value?.trim() || '',
        comptable: document.getElementById('mandat_comptable')?.value?.trim() || '',
        ej: document.getElementById('mandat_ej')?.value?.trim() || '',
        service: document.getElementById('mandat_service')?.value?.trim() || '',
        reference: document.getElementById('mandat_reference')?.value?.trim() || '',
    };
    try {
        const resp = await fetch('/mandat/save_checkout_data', {
            method: 'POST',
            headers: { 'Content-Type': 'application/json' },
            body: JSON.stringify({ jsonrpc: '2.0', method: 'call', id: 1, params }),
        });
        const data = await resp.json();
        return data?.result?.success !== false;
    } catch (e) {
        return false;
    }
}

patch(PaymentForm.prototype, {

    // Valide les champs mandat avant que la transaction Odoo soit créée
    async _initiatePaymentFlow(...args) {
        if (document.getElementById('mandat_administratif_form')) {
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
        }
        return super._initiatePaymentFlow(...args);
    },

    // Intercepte le redirect flow : si pas de formulaire de redirection → c'est mandat_administratif
    async _processRedirectFlow(...args) {
        if (!document.getElementById('o_payment_redirect_form')) {
            await saveMandatData();
            window.location.assign('/payment/status');
            return;
        }
        return super._processRedirectFlow(...args);
    },
});
