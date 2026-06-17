/** @odoo-module **/
import { PaymentForm } from '@payment/js/payment_form';
import { patch } from '@web/core/utils/patch';
import { rpc } from '@web/core/network/rpc';

patch(PaymentForm.prototype, {

    async submitForm() {
        const mandatForm = document.getElementById('mandat_administratif_form');
        const isMandatSelected = mandatForm && mandatForm.offsetParent !== null;

        if (isMandatSelected) {
            console.log("🎯 Interception Mandat Administratif lancée");
            
            const siret = document.getElementById('mandat_siret')?.value?.trim();
            const iban = document.getElementById('mandat_iban')?.value?.trim();
            const ordonnateur = document.getElementById('mandat_ordonnateur')?.value?.trim();
            const comptable = document.getElementById('mandat_comptable')?.value?.trim();
            const errorDiv = document.getElementById('mandat_form_error');

            if (!siret || !iban || !ordonnateur || !comptable) {
                if (errorDiv) errorDiv.style.display = 'block';
                // Réactiver le bouton de soumission natif d'Odoo
                this._enableSubmitButton?.(); 
                return; 
            }
            if (errorDiv) errorDiv.style.display = 'none';

            try {
                console.log("🔗 Envoi de la requête RPC au serveur...");
                
                // Appel au contrôleur Python
                const result = await rpc('/mandat/save_checkout_data', {
                    siret, iban, ordonnateur,
                    qualite: document.getElementById('mandat_qualite')?.value?.trim() || '',
                    comptable,
                    ej: document.getElementById('mandat_ej')?.value?.trim() || '',
                    service: document.getElementById('mandat_service')?.value?.trim() || '',
                    reference: document.getElementById('mandat_reference')?.value?.trim() || '',
                });

                console.log("✅ Réponse du serveur reçue :", result);
                console.log("🔄 Redirection vers /payment/status...");
                
                window.location.assign('/payment/status');
                return; // On coupe le flux Odoo définitivement

            } catch (rpcError) {
                console.error("❌ L'appel RPC ou la redirection a échoué :", rpcError);
                alert("Erreur technique lors de la sauvegarde du mandat. Vérifiez la console du navigateur ou les logs d'Odoo.sh.");
                this._enableSubmitButton?.(); // On redonne la main à l'utilisateur
                return;
            }
        }
        
        // Si ce n'est pas notre mandat, exécuter le comportement standard d'Odoo
        return super.submitForm(...arguments);
    },
});
