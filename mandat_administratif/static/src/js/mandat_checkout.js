/** @odoo-module **/
import { PaymentForm } from '@payment/js/payment_form';
import { patch } from '@web/core/utils/patch';
import { rpc } from '@web/core/network/rpc';

patch(PaymentForm.prototype, {

    async _updateSelectedPaymentOption() {
        await super._updateSelectedPaymentOption(...arguments);
    },

    async submitForm() {
        const data = this._getSelectedPaymentOptionData() || {};
        
        // Sécurité maximale : On va aussi chercher directement l'élément coché dans le DOM
        const checkedRadio = document.querySelector('input[name="o_payment_radio"]:checked');
        
        // On teste toutes les propriétés possibles d'Odoo 19 (CamelCase vs SnakeCase, Provider vs Method)
        const providerCode = data.providerCode 
            || data.provider_code 
            || checkedRadio?.dataset?.providerCode 
            || checkedRadio?.dataset?.provider_code;
            
        const paymentMethodCode = data.paymentMethodCode 
            || data.payment_method_code 
            || checkedRadio?.dataset?.paymentMethodCode 
            || checkedRadio?.dataset?.payment_method_code;

        console.log("--- DEBUG MANDAT ADMINISTRATIF ---");
        console.log("Data Odoo:", data);
        console.log("Provider Code détecté:", providerCode);
        console.log("Payment Method Code détecté:", paymentMethodCode);

        // Si l'un des codes correspond à notre mandat, on prend le contrôle exclusif
        if (providerCode === 'mandat_administratif' || paymentMethodCode === 'mandat_administratif') {
            console.log("👉 MANDAT DÉTECTÉ : Blocage du flux natif d'Odoo");
            
            const siret = document.getElementById('mandat_siret')?.value?.trim();
            const iban = document.getElementById('mandat_iban')?.value?.trim();
            const ordonnateur = document.getElementById('mandat_ordonnateur')?.value?.trim();
            const comptable = document.getElementById('mandat_comptable')?.value?.trim();
            const errorDiv = document.getElementById('mandat_form_error');

            // Validation des champs obligatoires
            if (!siret || !iban || !ordonnateur || !comptable) {
                if (errorDiv) errorDiv.style.display = 'block';
                console.log("❌ Formulaire incomplet");
                return; // On stoppe tout, on ne soumet rien
            }
            if (errorDiv) errorDiv.style.display = 'none';

            console.log("🚀 Envoi des données au contrôleur...");
            // Envoi des données au contrôleur backend
            await rpc('/mandat/save_checkout_data', {
                siret, iban, ordonnateur,
                qualite: document.getElementById('mandat_qualite')?.value?.trim() || '',
                comptable,
                ej: document.getElementById('mandat_ej')?.value?.trim() || '',
                service: document.getElementById('mandat_service')?.value?.trim() || '',
                reference: document.getElementById('mandat_reference')?.value?.trim() || '',
            });

            console.log("✅ Données sauvegardées, redirection...");
            // Redirection vers la page de statut/confirmation
            window.location.assign('/payment/status');
            return; // STRICTEMENT OBLIGATOIRE : évite de lancer le super.submitForm()
        }
        
        // Si ce n'est pas le mandat (Stripe, Paypal, etc.), on laisse Odoo gérer normalement
        return super.submitForm(...arguments);
    },
});
