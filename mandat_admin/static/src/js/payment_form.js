/** @odoo-module **/
import { PaymentForm } from '@payment/js/payment_form';
import { patch } from '@web/core/utils/patch';

patch(PaymentForm.prototype, {
    async _initiatePaymentFlow(provider, paymentOptionId, paymentMethodCode, flow) {
        if (provider === 'mandat_administratif') {
            const self = this;
            const processingValues = await self._getProcessingValues(
                provider, paymentOptionId, paymentMethodCode, flow
            );
            window.location.assign('/payment/status');
            return;
        }
        return super._initiatePaymentFlow(provider, paymentOptionId, paymentMethodCode, flow);
    },
});
