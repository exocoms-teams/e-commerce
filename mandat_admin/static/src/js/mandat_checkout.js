/** @odoo-module **/
import { PaymentForm } from '@payment/js/payment_form';
import { patch } from '@web/core/utils/patch';
import { jsonrpc } from '@web/core/network/rpc_service';

// Détecte si le radio "mandat_administratif" est sélectionné
// en cherchant la valeur dans TOUS les attributs data-* (indépendant du nommage camelCase/snake_case)
function isMandatSelected() {
    const radio = document.querySelector('input[name="o_payment_radio"]:checked');
    if (!radio) return false;
    return Array.from(radio.attributes).some(attr => attr.value === 'mandat_administratif');
}

// Flag : les données mandat ont été sauvegardées, on intercepte le redirect flow
let _mandatPaymentPending = false;

patch(PaymentForm.prototype, {

    // Affiche/masque le formulaire mandat selon le mode choisi
    async _updateSelectedPaymentOption() {
        await super._updateSelectedPaymentOption(...arguments);
        const form = document.getElementById('mandat_administratif_form');
        if (form) {
            form.style.display = isMandatSelected() ? 'block' : 'none';
        }
    },

    // Valide et sauvegarde les données mandat avant de laisser Odoo créer la transaction
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

            if (!result?.success) return;

            // Données sauvegardées : on laisse Odoo créer la transaction normalement,
            // puis on intercepte dans _processRedirectFlow avant le crash
            _mandatPaymentPending = true;
        }
        return super._initiatePaymentFlow(...args);
    },

    // Intercepte le redirect flow pour mandat_administratif (évite null.setAttribute)
    async _processRedirectFlow(...args) {
        if (_mandatPaymentPending) {
            _mandatPaymentPending = false;
            window.location.assign('/payment/status');
            return;
        }
        return super._processRedirectFlow(...args);
    },
});
