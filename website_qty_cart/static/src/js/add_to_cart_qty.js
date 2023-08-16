odoo.define('website_qty_cart.add_cart_qty', function (require) {
    'use strict';
    
    var core = require('web.core');
    var publicWidget = require('web.public.widget');
    var Dialog = require('web.Dialog');
    var _t = core._t;

    

    publicWidget.registry.WebsiteSale.include({
        events: _.extend({}, publicWidget.registry.WebsiteSale.prototype.events, {
            'click .add_to_cart_qty_cl': 'add_to_cart_qty',
            'click .a-minus-submit':'btnDisminucion',
            'click .a-plus-submit':'btnIncrement'
        }),
        add_to_cart_qty:function(ev){
            if ($("#is_seller_customer").val() == 'True') {
                var get_customer =  $("#customer").val()
                if (!get_customer){
                    var content = $('<div>').html(_t('<p>please select customer, for whom you want to purchase product!<p/>') );
                    new Dialog(self, {
                        title: _t('Warning!'),
                        size: 'medium',
                        $content: content,
                        buttons: [
                        {text: _t('Ok'), close: true}]
                    }).open();
                    ev.stopImmediatePropagation();
                    return false;
                }
            }

            var $input = $(ev.target).closest('.qty-card-input').find("#qty_cart");
            var $product_id = $(ev.target).closest('form').find("input[name='product_id']");
            var value = parseInt($input.val() || 0, 10);
            var add_product_id = parseInt($product_id.val(), 10);
            this._rpc({
                route: "/shop/cart/update_json",
                params: {
                    product_id: add_product_id,
                    add_qty: value,
                }
            }).then(function (data) {
                var $q = $(".my_cart_quantity");
                if (data.cart_quantity) {
                    $input.val(1)
                    _.each($(".my_cart_quantity"), function(qn){
                        $(qn).text(data.cart_quantity);
                    });
                }
            });
        },
        btnIncrement : function(ev){
            let $input = $(ev.target).closest('.qty-card-input').find("#qty_cart");
            let new_value = parseInt($input.val()) + 1 
            $input.val(new_value)
        },
        btnDisminucion : function(ev){
            let $input = $(ev.target).closest('.qty-card-input').find("#qty_cart");
            let new_value = parseInt($input.val())
            new_value =  new_value <= $input[0].min ? new_value = 1 : new_value -= 1
            $input.val(new_value)

        }
    });
})    