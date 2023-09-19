odoo.define('l10n_cl_pos_fe.OrderReceipt', function (require) {
    'use strict';

    const ReceiptOrder = require('point_of_sale.OrderReceipt');
    const Registries = require('point_of_sale.Registries');

    const FeReceiptOrder = (ReceiptOrder) =>
        class extends ReceiptOrder {
            async willStart() {
                var move = this.env.pos.validated_orders_name_server_id_map.account_move[0];
                try {
                    let searchReadRpc = await this.rpc({
                        model: 'account.move',
                        method: 'search_read',
                        args: [[['id', '=', move]], ['l10n_latam_document_number']],
                    });
                    this.env.pos.get_order().account_move = searchReadRpc[0].l10n_latam_document_number
                } catch(e) {
                    console.log(e);
                }

            }


        };

        Registries.Component.extend(ReceiptOrder, FeReceiptOrder);
        return FeReceiptOrder;
});