/** @odoo-module **/
import { PaymentForm } from '@payment/js/payment_form';
import { patch } from '@web/core/utils/patch';
import { jsonrpc } from '@web/core/network/rpc_service';

patch(PaymentForm.prototype, {

    // Affiche/masque le formulaire mandat selon le mode choisi
    async _updateSelectedPaymentOption() {
        await super._updateSelectedPaymentOption(...arguments);
        const selectedProvider = this._getSelectedPaymentOptionData()?.provider_code;
        const form = document.getElementById('mandat_administratif_form');
        if (form) {
            form.style.display = selectedProvider === 'mandat_administratif' ? 'block' : 'none';
        }
    },

    // Intercepte le paiement pour sauvegarder les champs mandat d'abord
    async _initiatePaymentFlow(...args) {
        const selectedProvider = this._getSelectedPaymentOptionData()?.provider_code;
        if (selectedProvider === 'mandat_administratif') {

            // Validation des champs obligatoires
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

            // Sauvegarde des données
            const result = await jsonrpc('/mandat/save_checkout_data', {
                siret,
                iban,
                ordonnateur,
                qualite: document.getElementById('mandat_qualite')?.value?.trim() || '',
                comptable,
                ej: document.getElementById('mandat_ej')?.value?.trim() || '',
                service: document.getElementById('mandat_service')?.value?.trim() || '',
                reference: document.getElementById('mandat_reference')?.value?.trim() || '',
            });

            if (!result?.success) {
                return;
            }

            // Redirige vers la page de statut
            window.location.assign('/payment/status');
            return;
        }
        return super._initiatePaymentFlow(...args);
    },
});
