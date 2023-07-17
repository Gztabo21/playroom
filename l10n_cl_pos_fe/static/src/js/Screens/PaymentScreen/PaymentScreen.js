odoo.define('l10n_cl_pos_fe.PaymentScreen', function (require) {
    'use strict';

    const PaymentScreen = require('point_of_sale.PaymentScreen');
    const Registries = require('point_of_sale.Registries');

    const FePaymentScreen = (PaymentScreen) =>
        class extends PaymentScreen {
            async willStart() {
                if (this.env.pos.config.module_ticket) {
                    await this.currentOrder.set_to_ticket(true);
                }
            }
            toggleIsToTicket() {
                var self = this;
                this.currentOrder.set_to_invoice(false)
                this.currentOrder.set_to_ticket(!this.currentOrder.is_to_ticket()).then(
                        function (){
                            self.get_caf();
                            self.render();
                        }
                    );
                    self.render();
            }
            toggleIsToInvoice() {
                var self = this;
                var client = self.env.pos.get_client()
                if (client.vat && client.l10n_cl_sii_taxpayer_type && client.l10n_cl_activity_description) {
                    this.unset_to_ticket()
                    this.currentOrder.set_to_invoice(!this.currentOrder.is_to_invoice()).then(
                        function (){
                            self.get_caf();
                            self.render();
                        }
                    );
                } else {
                    return self.showPopup('ErrorPopup',{
                        'title': self.env._t('Falta Informacion en el Cliente'),
                        'body': self.env._t('Verifique el RUT, direccion y tipo de contribuyente'),
                    });
                }
                self.render();
            }
            unset_to_ticket(){
                this.currentOrder.unset_to_ticket();
            }
            get_type_document() {
                var document = 'Ticket';
                if (this.currentOrder.to_invoice) {
                    document = 'FACTURA [33]';
                }
                if (this.currentOrder.to_ticket) {
                    document = 'BOLETA [39]';
                }
                return document;
            }
            get_caf() {
                const order = this.currentOrder;
                var caf = 0
                if (order.to_ticket || order.to_invoice){
                    caf = order.l10n_latam_document_number;
                }
                return caf;
            }
            async validateOrder(isForceValidate) {
                if (!this.currentOrder.get_client()){
                    alert("Debe seleccionar un cliente para la venta");
                }else{
                    if(this.env.pos.config.required_document){
                            if (!this.currentOrder.to_ticket && !this.currentOrder.to_invoice){
                                alert("Debe seleccionar un tipo de Documento antes de Validar la venta");
                            } else {
                                super.validateOrder(isForceValidate);
                            }
                        }else{
                            super.validateOrder(isForceValidate);
                        }
                }
            }
        };
        Registries.Component.extend(PaymentScreen, FePaymentScreen);
        return FePaymentScreen;

});
