odoo.define('wt_product_seller.customer', function (require) {
'use strict';

var core = require('web.core');
var publicWidget = require('web.public.widget');
var Dialog = require('web.Dialog');
var _t = core._t;

publicWidget.registry.websiteproductAddtoCart = publicWidget.Widget.extend({
    selector: '.js_sale',
    events: {
        'click .oe_product_cart': '_onAddtoCartClick',
        'click .product_order_history': '_onOrderHistoryClick',
        "change select[name='customer']": "on_change_customer"
    },
    start: function () {
        var self = this;
        return this._super.apply(this, arguments);
    },
    init: function () {
        this._super.apply(this, arguments);
        this._popoverRPC = null;
    },
    on_change_customer: function(ev){
        var customer_id = parseInt($(ev.currentTarget).val());
        this._rpc({
                    route: '/get_customer',
                    params: {
                        'customer': customer_id,
                    },
                }).then(function(result) {
                    window.location.reload();
                });
    },
    _onAddtoCartClick: function (ev) {
        var url = window.location.href.split('/')
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
    },
    _onOrderHistoryClick: function (ev) {
        $(this.selector).not(ev.currentTarget).popover('hide');

        var get_customer =  $("#customer").val();
        var $product_id = $(ev.target).closest('form').find("input[name='product_id']");
        var product_id = parseInt($product_id.val(), 10);
        this._rpc({
            route: '/customer/order/history',
            params: {
                'customer': get_customer,
                'product': product_id,
            },
        }).then(function(result) {
            var value = result;
            $('.product_history_popup').html(result.product_order_history);
            $("#product_quick_views_popup").modal('show');
            console.log('===========', value)
            
        });
    },
});

publicWidget.registry.WebsiteSale.include({
    events: _.extend({}, publicWidget.registry.WebsiteSale.prototype.events, {
        'click .add_to_cart_json_cl': 'add_to_cart_customer',
    }),
    add_to_cart_customer:function(ev){
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
        var $input = $(ev.target).closest('form').find("input[name='add_qty']");
        var $product_id = $(ev.target).closest('form').find("input[name='product_id']");
        var value = parseInt($input.val() || 0, 10);
        var add_product_id = parseInt($product_id.val(), 10);
        this._rpc({
            route: "/shop/cart/update_json",
            params: {
                product_id: add_product_id,
                add_qty: value,
            },
        }).then(function (data) {
            var $q = $(".my_cart_quantity");
            if (data.cart_quantity) {
                _.each($(".my_cart_quantity"), function(qn){
                    $(qn).text(data.cart_quantity);
                });
            }
        });
    },
});


});
