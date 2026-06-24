/** @odoo-module **/
import { PaymentForm } from '@payment/js/payment_form';
import { patch } from '@web/core/utils/patch';
import { onMounted } from '@odoo/owl';

// On connaît maintenant les noms exacts des attributs dataset Odoo 19
function isMandatSelected() {
    const radios = document.querySelectorAll('input[name="o_payment_radio"]');
    if (radios.length === 0) return !!document.getElementById('mandat_administratif_form');
    const radio = document.querySelector('input[name="o_payment_radio"]:checked');
    if (!radio) return false;
    return radio.dataset.providerCode === 'mandat_administratif'
        || radio.dataset.paymentMethodCode === 'mandat_administratif';
}

function updateMandatVisibility() {
    document.body.classList.toggle('o_mandat_active', isMandatSelected());
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

    async submitForm(...args) {
        if (!isMandatSelected()) return super.submitForm(...args);

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
            }
        } catch (e) {
            console.error('Mandat payment error:', e);
        }
    },
});
