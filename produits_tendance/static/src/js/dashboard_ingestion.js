/** @odoo-module **/

import publicWidget from "@web/legacy/js/public/public_widget";
import { rpc } from "@web/core/network/rpc";

publicWidget.registry.EbayIngestionWidget = publicWidget.Widget.extend({
    selector: '.o_winners_dashboard_header',
    
    events: {
        'click #btn_run_scan': '_onRunScanClick',
    },

    async _onRunScanClick(ev) {
        ev.preventDefault(); // Empêche tout rechargement inattendu
        
        var keyword = this.$('#ebay_keyword').val().trim();
        var $resultDiv = this.$('#scan_result');
        var $btn = this.$('#btn_run_scan');

        // 1. Vérification du champ
        if (!keyword) {
            $resultDiv.removeClass('d-none alert-success alert-danger')
                      .addClass('alert-warning')
                      .text('⚠️ Veuillez entrer un mot-clé.');
            return;
        }

        // 2. État de chargement visuel
        $btn.prop('disabled', true).text('⏳ Scan en cours... (patientez)');
        $resultDiv.addClass('d-none');

        // 3. Appel AJAX (RPC) moderne avec 'await'
        try {
            const data = await rpc('/dashboard/run_ebay_scan', {
                keyword: keyword
            });
            
            // 4. Succès de la requête
            $btn.prop('disabled', false).text("Lancer l'ingestion");
            $resultDiv.removeClass('d-none alert-warning alert-success alert-danger');
            
            if (data.status === 'success') {
                $resultDiv.addClass('alert-success')
                          .html('<strong>✅ Succès !</strong> ' + data.inserted + ' produits qualifiés ont été injectés.');
            } else {
                $resultDiv.addClass('alert-danger')
                          .html('<strong>❌ Erreur :</strong> ' + data.message);
            }
        } catch (error) {
            // 5. Erreur serveur ou réseau
            $btn.prop('disabled', false).text("Lancer l'ingestion");
            $resultDiv.removeClass('d-none alert-warning alert-success alert-danger')
                      .addClass('alert-danger')
                      .text('❌ Erreur de communication avec le serveur Odoo.');
            console.error("Erreur Ingestion:", error); // Utile pour déboguer avec F12
        }
    }
});