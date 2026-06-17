/** @odoo-module **/
import { PaymentForm } from '@payment/js/payment_form';
import { patch } from '@web/core/utils/patch';
import { rpc } from '@web/core/network/rpc';

patch(PaymentForm.prototype, {

    async _updateSelectedPaymentOption() {
        await super._updateSelectedPaymentOption(...arguments);
        const data = this._getSelectedPaymentOptionData();
        const form = document.getElementById('mandat_administratif_form');
        if (form) {
            form.style.display = data?.provider_code === 'mandat_administratif' ? 'block' : 'none';
        }
    },

    async submitForm() {
        const data = this._getSelectedPaymentOptionData();
        if (data?.provider_code === 'mandat_administratif') {
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

            await rpc('/mandat/save_checkout_data', {
                siret, iban, ordonnateur,
                qualite: document.getElementById('mandat_qualite')?.value?.trim() || '',
                comptable,
                ej: document.getElementById('mandat_ej')?.value?.trim() || '',
                service: document.getElementById('mandat_service')?.value?.trim() || '',
                reference: document.getElementById('mandat_reference')?.value?.trim() || '',
            });

            window.location.assign('/payment/status');
            return;
        }
        return super.submitForm(...arguments);
    },
});
