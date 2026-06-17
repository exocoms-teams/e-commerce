/** @odoo-module **/
import { PaymentForm } from '@payment/js/payment_form';
import { patch } from '@web/core/utils/patch';
import { rpc } from '@web/core/network/rpc';

patch(PaymentForm.prototype, {

    async _updateSelectedPaymentOption() {
        // On laisse Odoo afficher/masquer le formulaire inline de manière native
        await super._updateSelectedPaymentOption(...arguments);
    },

    async submitForm() {
        // ATTENTION : Odoo 19 utilise le camelCase 'providerCode'
        const data = this._getSelectedPaymentOptionData();

        console.log("MANDAT DATA =", data);

        if (data?.providerCode === 'mandat_administratif') {
            console.log("MANDAT DETECTE AVEC SUCCES");
            
            const siret = document.getElementById('mandat_siret')?.value?.trim();
            const iban = document.getElementById('mandat_iban')?.value?.trim();
            const ordonnateur = document.getElementById('mandat_ordonnateur')?.value?.trim();
            const comptable = document.getElementById('mandat_comptable')?.value?.trim();
            const errorDiv = document.getElementById('mandat_form_error');

            // Validation des champs obligatoires
            if (!siret || !iban || !ordonnateur || !comptable) {
                if (errorDiv) errorDiv.style.display = 'block';
                return; // Bloque la soumission
            }
            if (errorDiv) errorDiv.style.display = 'none';

            // Envoi des données au contrôleur backend
            await rpc('/mandat/save_checkout_data', {
                siret, iban, ordonnateur,
                qualite: document.getElementById('mandat_qualite')?.value?.trim() || '',
                comptable,
                ej: document.getElementById('mandat_ej')?.value?.trim() || '',
                service: document.getElementById('mandat_service')?.value?.trim() || '',
                reference: document.getElementById('mandat_reference')?.value?.trim() || '',
            });

            // Redirection propre vers le statut du paiement / confirmation
            window.location.assign('/payment/status');
            return; // On sort pour ÉVITER le super.submitForm() qui casserait le flux
        }
        
        // Pour tous les autres moyens de paiement (Stripe, Virement...), on utilise le comportement standard
        return super.submitForm(...arguments);
    },
});
