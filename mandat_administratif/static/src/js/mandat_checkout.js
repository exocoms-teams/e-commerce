/** @odoo-module **/

import publicWidget from "@web/legacy/js/public/public_widget";

/**
 * Applique la surcharge sur le formulaire de paiement d'Odoo
 * @param {Class} PaymentFormClass 
 */
function patchPaymentForm(PaymentFormClass) {
    if (PaymentFormClass.__mandatPatched) return;
    PaymentFormClass.__mandatPatched = true;

    console.log("⚡ [Mandat] Injection réussie dans le PaymentForm d'Odoo.");

    PaymentFormClass.include({
        /**
         * Surcharge de la soumission globale du formulaire
         * @override
         */
        async submitForm(ev) {
            const mandatForm = document.getElementById('mandat_administratif_form');
            const isMandatSelected = mandatForm && mandatForm.offsetParent !== null;

            if (isMandatSelected) {
                if (ev) {
                    ev.preventDefault();
                    ev.stopPropagation();
                }

                console.log("🎯 [Mandat] Flux intercepté avec succès.");

                const siret = document.getElementById('mandat_siret')?.value?.trim();
                const iban = document.getElementById('mandat_iban')?.value?.trim();
                const ordonnateur = document.getElementById('mandat_ordonnateur')?.value?.trim();
                const comptable = document.getElementById('mandat_comptable')?.value?.trim();
                const errorDiv = document.getElementById('mandat_form_error');

                // Validation des champs obligatoires
                if (!siret || !iban || !ordonnateur || !comptable) {
                    if (errorDiv) errorDiv.style.display = 'block';
                    if (typeof this._enableButton === 'function') this._enableButton();
                    return;
                }

                if (errorDiv) errorDiv.style.display = 'none';
                if (typeof this._disableButton === 'function') this._disableButton();

                // Envoi des données au contrôleur Python
                try {
                    const response = await fetch('/mandat/save_checkout_data', {
                        method: 'POST',
                        headers: { 'Content-Type': 'application/json' },
                        body: JSON.stringify({
                            jsonrpc: "2.0",
                            method: "call",
                            params: {
                                siret: siret,
                                iban: iban,
                                ordonnateur: ordonnateur,
                                qualite: document.getElementById('mandat_qualite')?.value?.trim() || '',
                                comptable: comptable,
                                ej: document.getElementById('mandat_ej')?.value?.trim() || '',
                                service: document.getElementById('mandat_service')?.value?.trim() || '',
                                reference: document.getElementById('mandat_reference')?.value?.trim() || ''
                            }
                        })
                    });

                    const result = await response.json();

                    if (result.error) {
                        console.error("Erreur backend:", result.error);
                        alert("Erreur serveur : " + (result.error.data?.message || result.error.message));
                        if (typeof this._enableButton === 'function') this._enableButton();
                        return;
                    }

                    window.location.assign('/payment/status');

                } catch (err) {
                    console.error("Erreur réseau :", err);
                    alert("Une erreur technique est survenue.");
                    if (typeof this._enableButton === 'function') this._enableButton();
                }
                
                // On coupe le flux ici pour empêcher la redirection native en échec d'Odoo
                return;
            }

            // Si c'est un autre moyen de paiement (Stripe, Paypal...), on laisse Odoo agir
            return this._super(...arguments);
        }
    });
}

// 🔥 LE PIÈGE SÉCURISÉ POUR LE LAZY-LOADING 🔥
// Si le formulaire est déjà chargé, on le patche immédiatement
if (publicWidget.registry.PaymentForm) {
    patchPaymentForm(publicWidget.registry.PaymentForm);
} else {
    // Sinon, on intercepte dynamiquement le moment précis où Odoo va l'injecter dans son registre
    Object.defineProperty(publicWidget.registry, 'PaymentForm', {
        configurable: true,
        enumerable: true,
        get: function () {
            return this._PaymentFormInstance;
        },
        set: function (val) {
            this._PaymentFormInstance = val;
            if (val) {
                patchPaymentForm(val);
            }
        }
    });
}
