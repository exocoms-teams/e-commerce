/** @odoo-module **/
import { PaymentForm } from '@payment/js/payment_form';
import { patch } from '@web/core/utils/patch';

patch(PaymentForm.prototype, {
    _processTokenizedFlow(providerCode, paymentOptionId, paymentMethodCode, processingValues) {
        if (providerCode === 'mandat_administratif') {
            window.location = '/payment/status';
            return;
        }
        return super._processTokenizedFlow(...arguments);
    },

    _processRedirectFlow(providerCode, paymentOptionId, paymentMethodCode, processingValues) {
        if (providerCode === 'mandat_administratif') {
            window.location = '/payment/status';
            return;
        }
        return super._processRedirectFlow(...arguments);
    },
});
