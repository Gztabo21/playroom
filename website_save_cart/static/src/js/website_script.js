odoo.define('website_save_cart.website_save_cart', function(require) {
  'use strict';
  var rpc = require('web.rpc');
  $(document).ready(function() {
    $('.sweet-click-delete-cart').click(function() {
      var cart_id = $(this).attr('data-cart_id');
      var closest_tr = $(this).closest('tr');
      swal({
          title: "Are you sure?",
          text: "You will not be able to recover this cart!",
          type: "warning",
          showCancelButton: true,
          confirmButtonClass: "btn-danger",
          confirmButtonText: "Yes, delete it!",
          cancelButtonText: "No, cancel!",
          closeOnConfirm: false,
          closeOnCancel: true
        },
        function(isConfirm) {
          if (isConfirm) {
            swal("Deleted!", "Your cart has been deleted.", "success");
            if (cart_id) {
              rpc.query({
                  model: 'save.cart',
                  method: 'unlink',
                  args: [parseInt(cart_id)],
                })
                .then(function(result) {
                  if (result === true) {
                    swal("Deleted!", "Your cart has been deleted.", "success");
                    window.location.href = '/my/carts';
                  }
                });
            }
          }
        });
    });
     $('.sweet-click-delete-cart-line').click(function() {
      var line_id = $(this).attr('data-line_id');
      var cart_id = $(this).attr('data-cart_id');
      var closest_tr = $(this).closest('tr');
      swal({
          title: "Are you sure?",
          text: "You will not be able to recover this cart!",
          type: "warning",
          showCancelButton: true,
          confirmButtonClass: "btn-danger",
          confirmButtonText: "Yes, delete it!",
          cancelButtonText: "No, cancel!",
          closeOnConfirm: false,
          closeOnCancel: true
        },
        function(isConfirm) {
          if (isConfirm) {
            swal("Deleted!", "Your cart has been deleted.", "success");
            if (line_id) {
              rpc.query({
                  model: 'save.cart.line',
                  method: 'unlink',
                  args: [parseInt(line_id)],
                })
                .then(function(result) {
                  if (result === true) {
                    swal("Deleted!", "Your cart has been deleted.", "success");
                    window.location.href = '/my/carts/' + cart_id;
                  }
                });
            }
          }
        });
    });
    $('.sweet-click-move-cart').click(function(){
      var cart_id = $(this).attr('data-cart_id');
      var closest_tr = $(this).closest('tr');
    });
    $('.save_carts_line_qty').change(function() {
      var line_id = $(this).attr('data-save-cart-line-id');
      var product_uom_qty = $(this).val();
      if (line_id) {
        rpc.query({
          model: 'save.cart.line',
          method: 'write',
          args: [parseInt(line_id), { product_uom_qty: product_uom_qty }],
        }).then(function(result) {
          location.reload();
        });
      }
    });
  });
});