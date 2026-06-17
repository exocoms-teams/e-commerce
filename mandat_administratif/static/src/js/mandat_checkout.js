/** @odoo-module **/
import publicWidget from '@web/legacy/js/public/public_widget';
import { rpc } from '@web/core/network/rpc';

publicWidget.registry.MandatCheckoutInterception = publicWidget.Widget.extend({
    selector: '.o_payment_form', // Cible directement le conteneur du formulaire de paiement d'Odoo
    events: {
        'click button[name="o_payment_submit_button"], click .o_payment_submit_button': '_onSubmitMandat',
    },

    async _onSubmitMandat(ev) {
        const mandatForm = document.getElementById('mandat_administratif_form');
        // Vérifie si notre formulaire de mandat est présent et visible à l'écran
        const isMandatSelected = mandatForm && mandatForm.offsetParent !== null;

        if (isMandatSelected) {
            // ACTION CRUCIALE : On stoppe immédiatement le clic pour empêcher le JS natif d'Odoo de s'exécuter
            ev.preventDefault();
            ev.stopImmediatePropagation();

            console.log("🎯 Mandat sélectionné : Interception du paiement réussie.");

            const siret = document.getElementById('mandat_siret')?.value?.trim();
            const iban = document.getElementById('mandat_iban')?.value?.trim();
            const ordonnateur = document.getElementById('mandat_ordonnateur')?.value?.trim();
            const comptable = document.getElementById('mandat_comptable')?.value?.trim();
            const errorDiv = document.getElementById('mandat_form_error');

            // Validation des champs requis
            if (!siret || !iban || !ordonnateur || !comptable) {
                if (errorDiv) errorDiv.style.display = 'block';
                console.log("❌ Formulaire incomplet.");
                return;
            }
            if (errorDiv) errorDiv.style.display = 'none';

            // Effet visuel de chargement sur le bouton pour l'utilisateur
            const $btn = $(ev.currentTarget);
            const originalHtml = $btn.html();
            $btn.attr('disabled', true).addClass('disabled').html('<i class="fa fa-spinner fa-spin"></i> Traitement en cours...');

            try {
                console.log("🔗 Envoi des données vers le contrôleur Python...");
                await rpc('/mandat/save_checkout_data', {
                    siret, iban, ordonnateur,
                    qualite: document.getElementById('mandat_qualite')?.value?.trim() || '',
                    comptable,
                    ej: document.getElementById('mandat_ej')?.value?.trim() || '',
                    service: document.getElementById('mandat_service')?.value?.trim() || '',
                    reference: document.getElementById('mandat_reference')?.value?.trim() || '',
                });

                console.log("✅ Données sauvegardées. Redirection vers le statut de paiement.");
                window.location.assign('/payment/status');

            } catch (rpcError) {
                console.error("❌ Erreur lors de la communication avec le serveur :", rpcError);
                alert("Une erreur technique est survenue lors de la validation de votre mandat. Veuillez réessayer.");
                // En cas d'erreur, on réactive le bouton pour que l'utilisateur puisse recliquer
                $btn.attr('disabled', false).removeClass('disabled').html(originalHtml);
            }
        }
    }
});
