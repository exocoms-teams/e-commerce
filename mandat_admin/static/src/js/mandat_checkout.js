/** @odoo-module **/
import { PaymentForm } from '@payment/js/payment_form';
import { patch } from '@web/core/utils/patch';

function isMandatSelected() {
    const radio = document.querySelector('input[name="o_payment_radio"]:checked');
    if (!radio) {
        // Pas de radio = provider unique, c'est le nôtre si notre form existe
        return !!document.getElementById('mandat_administratif_form');
    }
    // Vérifie tous les attributs data-* pour la valeur 'mandat_administratif'
    for (const val of Object.values(radio.dataset)) {
        if (val === 'mandat_administratif') return true;
    }
    // Fallback fiable : vérifie le texte visible de l'option sélectionnée
    const container = radio.closest('li, label, .o_payment_option, [class*="payment"]') || radio.parentElement;
    return container?.textContent?.toLowerCase().includes('mandat') || false;
}

// Injecte #o_payment_redirect_form pointant vers notre contrôleur
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

    // Affiche/masque le formulaire mandat selon le provider sélectionné
    async _updateSelectedPaymentOption() {
        await super._updateSelectedPaymentOption(...arguments);
        const mandatForm = document.getElementById('mandat_administratif_form');
        if (!mandatForm) return;
        if (isMandatSelected()) {
            mandatForm.style.display = 'block';
            injectMandatRedirectForm();
        } else {
            mandatForm.style.display = 'none';
            removeMandatRedirectForm();
        }
    },

    // Valide les champs et sauvegarde les données avant la transaction
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

            // Assure que le formulaire de redirection est injecté avant que super() ne le cherche
            injectMandatRedirectForm();
        }
        return super._initiatePaymentFlow(...args);
    },

    // Filet de sécurité si le formulaire de redirection est absent
    async _processRedirectFlow(...args) {
        if (!document.getElementById('o_payment_redirect_form')) {
            window.location.assign('/mandat/payment_confirm');
            return;
        }
        return super._processRedirectFlow(...args);
    },
});
