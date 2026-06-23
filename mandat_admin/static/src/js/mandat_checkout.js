/** @odoo-module **/
import { PaymentForm } from '@payment/js/payment_form';
import { patch } from '@web/core/utils/patch';
import { jsonrpc } from '@web/core/network/rpc_service';

patch(PaymentForm.prototype, {

    // Affiche/masque le formulaire mandat selon le mode choisi
    async _updateSelectedPaymentOption() {
        await super._updateSelectedPaymentOption(...arguments);
        const radio = document.querySelector('input[name="o_payment_radio"]:checked');
        // Cherche 'mandat_administratif' dans tous les attributs data-* (indépendant du nommage Odoo)
        const isMandat = radio && Array.from(radio.attributes).some(a => a.value === 'mandat_administratif');
        const form = document.getElementById('mandat_administratif_form');
        if (form) {
            form.style.display = isMandat ? 'block' : 'none';
        }
    },

    // Valide et sauvegarde si le formulaire mandat est visible, puis laisse Odoo continuer
    async _initiatePaymentFlow(...args) {
        const mandatForm = document.getElementById('mandat_administratif_form');
        const isMandatVisible = mandatForm && window.getComputedStyle(mandatForm).display !== 'none';

        if (isMandatVisible) {
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

            // Données sauvegardées → on laisse super créer la transaction,
            // puis on intercepte dans _processRedirectFlow
        }
        return super._initiatePaymentFlow(...args);
    },

    // Filet de sécurité final : si _processRedirectFlow est appelé sans formulaire de redirection,
    // c'est forcément notre provider (Odoo ne rend pas #o_payment_redirect_form pour mandat_administratif)
    async _processRedirectFlow(...args) {
        const redirectForm = document.getElementById('o_payment_redirect_form');
        if (!redirectForm) {
            // Tentative de sauvegarde des données si pas encore fait
            const siret = document.getElementById('mandat_siret')?.value?.trim();
            if (siret) {
                try {
                    await jsonrpc('/mandat/save_checkout_data', {
                        siret,
                        iban: document.getElementById('mandat_iban')?.value?.trim() || '',
                        ordonnateur: document.getElementById('mandat_ordonnateur')?.value?.trim() || '',
                        qualite: document.getElementById('mandat_qualite')?.value?.trim() || '',
                        comptable: document.getElementById('mandat_comptable')?.value?.trim() || '',
                        ej: document.getElementById('mandat_ej')?.value?.trim() || '',
                        service: document.getElementById('mandat_service')?.value?.trim() || '',
                        reference: document.getElementById('mandat_reference')?.value?.trim() || '',
                    });
                } catch (e) {}
            }
            window.location.assign('/payment/status');
            return;
        }
        return super._processRedirectFlow(...args);
    },
});
