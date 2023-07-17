odoo.define("presale.website_save_cart", function (require) {
  "use strict";
  var rpc = require("web.rpc");
  $(document).ready(function () {
    $(".sweet-click-union-cart").click(function () {
      var save_cart_ids = $(this).attr("save_cart_ids");
      var closest_tr = $(this).closest("tr");
      swal(
        {
          title: "Estas Seguro?",
          text: "No recuperaras los carros guardados actualmente!",
          type: "warning",
          showCancelButton: true,
          confirmButtonClass: "btn-danger",
          confirmButtonText: "Si, mezclarlos!",
          cancelButtonText: "No, cancelar!",
          closeOnConfirm: false,
          closeOnCancel: true,
        },
        function (isConfirm) {
          if (isConfirm) {
            if (save_cart_ids) {
              rpc
                .query({
                  model: "save.cart",
                  method: "union_save_carts",
                  args: [save_cart_ids],
                })
                .then(function (result) {
                  console.log(result);
                  if (result == true) {
                    swal(
                      "Hecho!",
                      "Tus carros han sido reasignados en uno solo.",
                      "success"
                    );
                    window.location.href = "/my/carts";
                  } else {
                    swal(
                      "Alerta!",
                      "Tus carritos no han podido ser mezclados.",
                      "error"
                    );
                  }
                });
            }
          }
        }
      );
    });
  });
});
