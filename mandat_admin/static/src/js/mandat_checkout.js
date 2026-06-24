/** @odoo-module **/
import { PaymentForm } from '@payment/js/payment_form';
import { patch } from '@web/core/utils/patch';

patch(PaymentForm.prototype, {

    // Intercepte Pay Now avant toute la chaîne de paiement Odoo
    async submitForm(...args) {
        const mandatForm = document.getElementById('mandat_administratif_form');
        if (!mandatForm) return super.submitForm(...args);

        // Détection : radio checké OU provider unique (pas de radio)
        const radio = document.querySelector('input[name="o_payment_radio"]:checked');
        const allRadios = document.querySelectorAll('input[name="o_payment_radio"]');

        let isMandat = allRadios.length === 0; // provider unique
        if (!isMandat && radio) {
            // Essaie tous les attributs data-*
            for (const val of Object.values(radio.dataset)) {
                if (val === 'mandat_administratif') { isMandat = true; break; }
            }
            // Fallback : texte visible
            if (!isMandat) {
                const container = radio.closest('li, label, .o_payment_option, [class*="payment"]') || radio.parentElement;
                isMandat = container?.textContent?.toLowerCase().includes('mandat') || false;
            }
        }

        if (!isMandat) return super.submitForm(...args);

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

        // Sauvegarde + création transaction + redirect, tout via un seul appel
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
