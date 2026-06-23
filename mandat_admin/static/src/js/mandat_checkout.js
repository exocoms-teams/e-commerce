/** @odoo-module **/
import { PaymentForm } from '@payment/js/payment_form';
import { patch } from '@web/core/utils/patch';
import { rpc } from '@web/core/network/rpc';
import { onMounted } from '@odoo/owl';

function showMandatFormIfSelected() {
    const form = document.getElementById('mandat_administratif_form');
    if (!form) return;

    const radios = document.querySelectorAll('input[name="o_payment_radio"]');
    if (radios.length === 0) {
        // Seul provider disponible → afficher directement
        form.style.display = 'block';
        return;
    }
    const radio = document.querySelector('input[name="o_payment_radio"]:checked');
    const isMandat = radio && Array.from(radio.attributes).some(a => a.value === 'mandat_administratif');
    form.style.display = isMandat ? 'block' : 'none';
}

patch(PaymentForm.prototype, {

    setup() {
        super.setup(...arguments);
        // Affiche le formulaire mandat dès le montage du composant
        onMounted(() => showMandatFormIfSelected());
    },

    async _updateSelectedPaymentOption() {
        await super._updateSelectedPaymentOption(...arguments);
        showMandatFormIfSelected();
    },

    async _initiatePaymentFlow(...args) {
        const mandatForm = document.getElementById('mandat_administratif_form');
        if (!mandatForm) return super._initiatePaymentFlow(...args);

        const radios = document.querySelectorAll('input[name="o_payment_radio"]');
        const noRadios = radios.length === 0;
        const isVisible = window.getComputedStyle(mandatForm).display !== 'none';

        if (noRadios || isVisible) {
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

            const result = await rpc('/mandat/save_checkout_data', {
                siret,
                iban,
                ordonnateur,
                qualite: document.getElementById('mandat_qualite')?.value?.trim() || '',
                comptable,
                ej: document.getElementById('mandat_ej')?.value?.trim() || '',
                service: document.getElementById('mandat_service')?.value?.trim() || '',
                reference: document.getElementById('mandat_reference')?.value?.trim() || '',
            });

            if (!result?.success) return;

            window.location.assign('/payment/status');
            return;
        }

        return super._initiatePaymentFlow(...args);
    },

    // Filet de sécurité : #o_payment_redirect_form absent → notre provider
    async _processRedirectFlow(...args) {
        const redirectForm = document.getElementById('o_payment_redirect_form');
        if (!redirectForm) {
            window.location.assign('/payment/status');
            return;
        }
        return super._processRedirectFlow(...args);
    },
});
