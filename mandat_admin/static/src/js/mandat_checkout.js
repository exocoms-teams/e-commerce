/** @odoo-module **/
import { PaymentForm } from '@payment/js/payment_form';
import { patch } from '@web/core/utils/patch';
import { onMounted } from '@odoo/owl';

function isMandatSelected() {
    const radios = document.querySelectorAll('input[name="o_payment_radio"]');
    if (radios.length === 0) {
        return !!document.getElementById('mandat_administratif_form');
    }
    const radio = document.querySelector('input[name="o_payment_radio"]:checked');
    if (!radio) return false;
    for (const val of Object.values(radio.dataset)) {
        if (val === 'mandat_administratif') return true;
    }
    const container = radio.closest('li, label, .o_payment_option, [class*="payment"]') || radio.parentElement;
    return container?.textContent?.toLowerCase().includes('mandat') || false;
}

// Contrôle la visibilité via une classe CSS sur body (survit aux re-renders OWL)
function updateMandatVisibility() {
    document.body.classList.toggle('o_mandat_active', isMandatSelected());
    if (isMandatSelected()) {
        injectMandatRedirectForm();
    } else {
        removeMandatRedirectForm();
    }
}

function injectMandatRedirectForm() {
    if (document.getElementById('o_payment_redirect_form')) return;
    const form = document.createElement('form');
    form.id = 'o_payment_redirect_form';
    form.action = '/mandat/payment_confirm';
    form.method = 'get';
    form.style.display = 'none';
    form.dataset.mandatInjected = 'true';
    document.body.appendChild(form);
}

function removeMandatRedirectForm() {
    const form = document.getElementById('o_payment_redirect_form');
    if (form?.dataset?.mandatInjected) form.remove();
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

    async _initiatePaymentFlow(...args) {
        if (isMandatSelected()) {
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
                await fetch('/mandat/save_checkout_data', {
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
            } catch (e) {}

            injectMandatRedirectForm();
        }
        return super._initiatePaymentFlow(...args);
    },

    async _processRedirectFlow(...args) {
        if (!document.getElementById('o_payment_redirect_form')) {
            window.location.assign('/mandat/payment_confirm');
            return;
        }
        return super._processRedirectFlow(...args);
    },
});
