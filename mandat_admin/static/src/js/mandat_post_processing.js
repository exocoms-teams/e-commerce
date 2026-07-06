/** @odoo-module **/
import { PaymentPostProcessing } from '@payment/interactions/post_processing';
import { patch } from '@web/core/utils/patch';

patch(PaymentPostProcessing, {
    getFinalStates(providerCode) {
        const finalStates = super.getFinalStates(...arguments);
        if (providerCode === 'mandat_administratif') {
            finalStates.add('pending');
        }
        return finalStates;
    },
});
