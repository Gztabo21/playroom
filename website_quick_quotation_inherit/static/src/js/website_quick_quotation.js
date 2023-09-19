odoo.define(
  "website_quick_quotation_inherit.quick_quotation",
  function (require) {
    "use strict";

    var core = require("web.core");
    var publicWidget = require("web.public.widget");
    var rpc = require("web.rpc");
    var _t = core._t;
    console.log("entrando por aca");
    var session = require("web.session");

    $(document).ready(function () {
      //   const partner_wesbite = document.querySelector("#partner_wesbite");
      //   console.log("*****");
      //   console.log(partner_wesbite);

      $("#partner_section")
        .find("select")
        .each(function () {
          if (!$(this).data("select2")) {
            $(this).select2({
              width: "100%",
              placeholder: "Seleccionar Tercero",
              allowClear: true,
            });
          }
        });
    });

    publicWidget.registry.quick_quotation = publicWidget.Widget.include({
      selector: "#wrapwrap:has(.o_quick_quotation)",
      events: {
        "click .add-new-line": _.debounce(
          function (e) {
            this.add_new_roww(e);
          },
          200,
          true
        ),

        "click .add": _.debounce(
          function (e) {
            this.add_row(e);
          },
          200,
          true
        ),

        "click .edit": _.debounce(
          function (e) {
            this.edit_row(e);
          },
          200,
          true
        ),

        "click .delete": _.debounce(
          function (e) {
            this.delete_row(e);
          },
          200,
          true
        ),

        "change select#product": _.debounce(
          function (e) {
            this.on_change_product(e);
          },
          200,
          true
        ),

        "change select#partner_website": _.debounce(
          function (e) {
            this.willStart(e);
            //this.start(e);
            this.load_data_product(e);
            this.on_search_prodcuts(e);
            //this.remove_row_onchange(e);
          },
          200,
          true
        ),

        "change .quantity": _.debounce(
          function (e) {
            this.on_change_quantity(e);
          },
          200,
          true
        ),

        "click .submit": _.debounce(
          function (e) {
            this.on_click_submit(e);
          },
          200,
          true
        ),

        "keyup .search_prodcuts": "on_search_prodcuts",
      },

      willStart: function () {
        var self = this;
        var def = this._super.apply(this, arguments);

        // var def1 = this._rpc({
        //   route: "/website_quick_quotation/get_products_data",
        //   args: [[session.user_context], 1],
        //   //   params: {
        //   //     context: session.user_context,
        //   //     user_id: this.userId,
        //   // },
        // }).then(function (res) {
        //   self.products = res;
        // });
        var partner_website = document.querySelector("#partner_website");
        var partner_id = 1;
        if (partner_website) {
          partner_id = partner_website.value;
        }

        var def1 = this._rpc({
          route: "/website_quick_quotation/load_products_data",
          params: {
            partner_id: partner_id,
          },
        }).then(function (res) {
          self.products = res;
        });

        return Promise.all([def, def1]);
      },

      init: function (parent, options) {
        this._super.apply(this, arguments);
      },

      start: function () {
        var self = this;
        return this._super.apply(this, arguments).then(function () {
          $(".submit").attr("disabled", "disabled");
          $(".search_prodcuts").attr("disabled", "disabled");
        });
      },

      //   start_table: function () {
      //     var self = this;
      //     return this._super.apply(this, arguments).then(function () {
      //       $(".submit").attr("disabled", "disabled");
      //       $(".search_prodcuts").attr("disabled", "disabled");
      //     });
      //   },

      load_data_product: function (e) {
        e.preventDefault();
        e.stopPropagation();
        // var $target = $(e.currentTarget);
        // $target.attr("disabled", "disabled");
        var index = $("table tbody tr:last-child").index();
        // this.actions =
        //   '<a class="add" title="Add" data-toggle="tooltip">' +
        //   '<i class="fa fa-check"></i>' +
        //   "</a>" +
        //   '<a class="edit" title="Edit" data-toggle="tooltip">' +
        //   '<i class="fa fa-edit"></i>' +
        //   "</a>" +
        //   '<a class="delete" title="Delete" data-toggle="tooltip">' +
        //   '<i class="fa fa-trash"></i>' +
        //   "</a>";

        this.actions = `
          
        <a class="add" title="Add" data-toggle="tooltip">
          <i class="fa fa-check"></i>
        </a>

        <a class="edit" title="Edit" data-toggle="tooltip"> 
          <i class="fa fa-edit"></i>
        </a>

        <a class="delete" title="Delete" data-toggle="tooltip">
          <i class="fa fa-trash"></i> 
        </a>
        
        `;

        var row = "";
        row += "<tr>";
        row += "<td></td>";
        row += `
        <td>
            <select type="text" class="form-control product" name="product" id="product">
            <option></option>
        `;

        for (let i = 0; i < this.products.length; i++) {
          // row +=
          //   '<option t-att-value="product_price" data-id="' +
          //   this.products[i]["id"] +
          //   '" data-unit="' +
          //   this.products[i]["uom_id"] +
          //   '" data-price="' +
          //   this.products[i]["price"] +
          //   '"> <span t-esc="product_price"/>' +
          //   this.products[i]["name"] +
          //   "</option>";

          const product_product_id = this.products[i]["id"];
          const product_name = this.products[i]["name"];
          //row += `<t t-set="product_price" t-value="current_pricelist_quotation.get_product_price(product_sudo.search([("id", "=", ${product_product_id})], limit=1))" />`;
          const product_uom = this.products[i]["uom_id"];
          const product_price = this.products[i]["price"];
          const product_total = this.products[i]["total"];

          row += `
          <option data-id="${product_product_id}" data-unit="${product_uom}" data-price="${product_price}" data-total="${product_total}"> 
            ${product_name} 
          </option>
          `;
        }
        // row += "</select></td>";
        // row += '<td><span class="unit" name="unit" id="unit"></span></td>';
        // row += '<td><span class="price" name="price" id="price"></span></td>';
        // row +=
        //   '<td><input type="text" class="form-control quantity" name="quantity" id="quantity"></td>';
        // row += "<td>" + this.actions + "</td>";
        // row += "</tr>";

        row += `
          </select>
        </td>
        <td>
          <span class="unit" name="unit" id="unit"></span>
        </td>
        <td>
          <input type="text" class="form-control quantity" name="quantity" id="quantity">
        </td>
        <td>
          <span class="price" name="price" id="price"></span>
        </td>
        <td>
          <span class="total" name="total" id="total"></span>
        </td>
        <td>${this.actions}</td>
      </tr>
      
      `;

        $(".table_quick_quotation").append(row);
        $("table tbody tr")
          .eq(index + 1)
          .find(".add, .edit")
          .toggle();

        this.add_row_number($("#table_quick_quotation"));

        $("#table_quick_quotation")
          .find("select")
          .each(function () {
            if (!$(this).data("select2")) {
              $(this).select2({
                width: "100%",
                placeholder: "Seleccionar Producto",
                allowClear: true,
              });
            }
          });

        $(".add-new-line").removeAttr("disabled");
      },

      add_new_roww: function (e) {
        e.preventDefault();
        e.stopPropagation();
        var $target = $(e.currentTarget);
        $target.attr("disabled", "disabled");
        var index = $("table tbody tr:last-child").index();
        // this.actions =
        //   '<a class="add" title="Add" data-toggle="tooltip">' +
        //   '<i class="fa fa-check"></i>' +
        //   "</a>" +
        //   '<a class="edit" title="Edit" data-toggle="tooltip">' +
        //   '<i class="fa fa-edit"></i>' +
        //   "</a>" +
        //   '<a class="delete" title="Delete" data-toggle="tooltip">' +
        //   '<i class="fa fa-trash"></i>' +
        //   "</a>";

        this.actions = `
          
        <a class="add" title="Add" data-toggle="tooltip">
          <i class="fa fa-check"></i>
        </a>

        <a class="edit" title="Edit" data-toggle="tooltip"> 
          <i class="fa fa-edit"></i>
        </a>

        <a class="delete" title="Delete" data-toggle="tooltip">
          <i class="fa fa-trash"></i> 
        </a>
        
        `;

        var row = "";
        row += "<tr>";
        row += "<td></td>";
        row += `
        <t t-set="current_pricelist_quotation" t-value="website.get_current_pricelist()" />
        <t t-set="product_sudo" t-value="request.env["product.product"].sudo()" />

        <td>
            <select type="text" class="form-control product" name="product" id="product">
            <option></option>
        `;

        for (let i = 0; i < this.products.length; i++) {
          //const product_product_id = this.products[i]["id"];

          //row += `<t t-set="product_price" t-value="current_pricelist_quotation.get_product_price(product_sudo.search([("id", "=", ${product_product_id})], limit=1))" />`;
          // row +=
          //   '<option t-att-value="product_price" data-id="' +
          //   this.products[i]["id"] +
          //   '" data-unit="' +
          //   this.products[i]["uom_id"] +
          //   '" data-price="' +
          //   this.products[i]["price"] +
          //   '"> <span t-esc="product_price"/>' +
          //   this.products[i]["name"] +
          //   "</option>";
          const product_product_id = this.products[i]["id"];
          const product_name = this.products[i]["name"];
          //row += `<t t-set="product_price" t-value="current_pricelist_quotation.get_product_price(product_sudo.search([("id", "=", ${product_product_id})], limit=1))" />`;
          const product_uom = this.products[i]["uom_id"];
          const product_price = this.products[i]["price"];
          const product_total = this.products[i]["total"];

          row += `
          <option data-id="${product_product_id}" data-unit="${product_uom}" data-price="${product_price}" data-total="${product_total}"> 
            ${product_name} 
          </option>
          `;
        }
        // row += "</select></td>";
        // row += '<td><span class="unit" name="unit" id="unit"></span></td>';
        // row += '<td><span class="price" name="price" id="price"></span></td>';
        // row +=
        //   '<td><input type="text" class="form-control quantity" name="quantity" id="quantity"></td>';
        // row += "<td>" + this.actions + "</td>";
        // row += "</tr>";

        row += `
            </select>
          </td>
          <td>
            <span class="unit" name="unit" id="unit"></span>
          </td>
          <td>
            <input type="text" class="form-control quantity" name="quantity" id="quantity">
          </td>
          <td>
            <span class="price" name="price" id="price"></span>
          </td>
          <td>
            <span class="total" name="total" id="total"></span>
          </td>
          <td>${this.actions}</td>
        </tr>
    
    `;

        $(".table_quick_quotation").append(row);
        $("table tbody tr")
          .eq(index + 1)
          .find(".add, .edit")
          .toggle();

        this.add_row_number($("#table_quick_quotation"));

        $("#table_quick_quotation")
          .find("select")
          .each(function () {
            if (!$(this).data("select2")) {
              $(this).select2({
                width: "100%",
                placeholder: "Seleccionar Producto",
                allowClear: true,
              });
            }
          });

        this.check_row_number($("#table_quick_quotation"));
      },

      add_row_number: function ($table) {
        var count = 0;
        $table.find("tbody tr").each(function (index, el) {
          $(el)
            .find("td:eq(0)")
            .html(++count + ".");
        });
      },

      check_row_number: function ($table) {
        var count = 0;
        $table.find("tbody tr").each(function (index, el) {
          count = count + 1;
        });
        if (count > 0) {
          $(".submit").removeAttr("disabled");
          $(".search_prodcuts").removeAttr("disabled");
        } else {
          $(".submit").attr("disabled", "disabled");
          $(".search_prodcuts").attr("disabled", "disabled");
        }
      },

      remove_row_onchange: function (e) {
        e.preventDefault();
        var $target = $(e.currentTarget);
        var $row = $target.parents("tr");
        if ($row) {
          $row.remove();
        }
      },

      delete_row_number: function (e) {
        e.preventDefault();
        var $target = $(e.currentTarget);
        var $row = $target.parents("tr");
        if ($row) {
          $row.remove();
          this.add_row_number($("#table_quick_quotation"));
        }
        this.check_row_number($("#table_quick_quotation"));
      },

      add_row: function (e) {
        e.preventDefault();
        e.stopPropagation();
        var select_empty = false;
        var input_empty = false;

        var $target = $(e.currentTarget);
        var $select = $target.parents("tr").find("select");
        var $input = $target.parents("tr").find("input");

        $select.each(function () {
          if (!$(this).val()) {
            $(this).addClass("error");
            select_empty = true;
          } else {
            $(this).removeClass("error");
            select_empty = false;
          }
        });

        $input.each(function () {
          if (!$(this).val()) {
            $(this).addClass("error");
            input_empty = true;
          } else {
            $(this).removeClass("error");
            input_empty = false;
          }
        });
        $target.parents("tr").find(".error").first().focus();

        if (!select_empty && !input_empty) {
          $target
            .parents("tr")
            .find("select")
            .each(function () {
              if ($(this).getAttributes()["id"] == "product") {
                $(this).attr("disabled", "disabled");
              }
            });
          $target
            .parents("tr")
            .find("input")
            .each(function () {
              if ($(this).getAttributes()["id"] == "quantity") {
                $(this).attr("disabled", "disabled");
              }
            });

          $target.parents("tr").find(".add, .edit").toggle();
          $(".add-new-line").removeAttr("disabled");
        }
      },

      edit_row: function (e) {
        e.preventDefault();
        e.stopPropagation();
        var $target = $(e.currentTarget);

        $target
          .parents("tr")
          .find("select")
          .each(function () {
            if ($(this).getAttributes()["id"] == "product") {
              $(this).removeAttr("disabled", "disabled");
            }
          });
        $target
          .parents("tr")
          .find("input")
          .each(function () {
            if ($(this).getAttributes()["id"] == "quantity") {
              $(this).removeAttr("disabled", "disabled");
            }
          });

        $target.parents("tr").find(".add, .edit").toggle();
        $(".add-new-line").attr("disabled", "disabled");
      },

      delete_row: function (e) {
        e.preventDefault();
        e.stopPropagation();
        var $target = $(e.currentTarget);
        $target.parents("tr").remove();
        $(".add-new-line").removeAttr("disabled");

        this.delete_row_number(e);
      },

      on_change_product: function (e) {
        e.preventDefault();
        e.stopPropagation();
        var $target = $(e.currentTarget);
        var $select = $target.parents("tr").find("select[name='product']");

        var $unit = $target.parents("tr").find("span[name='unit']");
        var unit = $select.children(":selected").data("unit");

        var $price = $target.parents("tr").find("span[name='price']");
        var price = $select.children(":selected").data("price");

        var $total = $target.parents("tr").find("span[name='total']");
        var total = $select.children(":selected").data("total");

        if (unit != null) {
          $unit[0].innerHTML = unit.split(",")[1];
        } else {
          $unit[0].innerHTML = "";
        }

        if (price != null) {
          $price[0].innerHTML = price;
        } else {
          $price[0].innerHTML = "";
        }

        if (total != null) {
          $total[0].innerHTML = total;
        } else {
          $total[0].innerHTML = "";
        }
      },

      on_change_quantity: function (e) {
        e.preventDefault();
        e.stopPropagation();
        var $target = $(e.currentTarget);
        var quantity = $target.val();
        if (isNaN(quantity)) {
          $target.val("");
        }

        var $select = $target.parents("tr").find("select[name='product']");

        var $price = $target.parents("tr").find("span[name='price']");
        var price = $select.children(":selected").data("price");

        var $total = $target.parents("tr").find("span[name='total']");

        if (price != null) {
          $total[0].innerHTML = quantity * price;
        } else {
          $total[0].innerHTML = "";
        }

        this.return_sum_total(e);
      },

      return_sum_total: function (e) {
        e.preventDefault();
        e.stopPropagation();
        var self = this;
        var $table = $(".table_quick_quotation");

        var data = [];

        console.log("Calculando el total vea");
        $table.find("tbody tr").each(function () {
          var $selected = $(this).find("select[name='product']");
          var product_id = $selected.children(":selected").data("id");
          var product_price = $selected.children(":selected").data("price");

          console.log("Product");
          console.log(product_id);

          var $quantity = $(this).find("input[name='quantity']");
          var qty = $quantity.val();

          console.log("Qty");
          console.log(qty);

          console.log("Product Price");
          console.log(product_price);

          if (product_id) {
            var vals = {
              product_id,
              qty: parseInt(qty),
              product_price,
              total: product_price * parseInt(qty),
            };

            data.push(vals);
          }
        });

        if (data.length > 0) {
          var sum_total = 0;
          console.log(data);
          var $target = $(e.currentTarget);
          var $information_total = $target.find(
            "span[name='information_total']"
          );

          var information_total = $information_total.data("information_total");

          data.forEach((element) => {
            sum_total += element.total;
          });
          console.log("Total general");
          console.log(sum_total);

          // if (information_total != null) {
          //   $information_total[0].innerHTML = sum_total;
          // } else {
          //   $information_total[0].innerHTML = "0";
          // }
        }
      },

      on_click_submit: function (e) {
        e.preventDefault();
        e.stopPropagation();

        var self = this;

        var name_empty = false;
        var email_empty = false;

        var select_empty = false;
        var input_empty = false;

        var $name = $(".input_name");
        var $email = $(".input_email");
        //var $partner_id = $(".input_partner_id");

        // if ($name) {
        //   if (!$name.val()) {
        //     $name.addClass("error");
        //     name_empty = true;
        //   } else {
        //     $name.removeClass("error");
        //     name_empty = false;
        //   }
        // }

        // if ($email) {
        //   if (!$email.val()) {
        //     $email.addClass("error");
        //     email_empty = true;
        //   } else {
        //     $email.removeClass("error");
        //     email_empty = false;
        //   }
        // }

        var $table = $(".table_quick_quotation");
        var $select = $table.find("tr").find("select");
        var $input = $table.find("tr").find("input");

        // $select.each(function () {
        //   if (!$(this).val()) {
        //     $(this).addClass("error");
        //     select_empty = true;
        //   } else {
        //     $(this).removeClass("error");
        //     select_empty = false;
        //   }
        // });

        // $input.each(function () {
        //   if (!$(this).val()) {
        //     $(this).addClass("error");
        //     input_empty = true;
        //   } else {
        //     $(this).removeClass("error");
        //     input_empty = false;
        //   }
        // });

        //if (!select_empty && !input_empty && !name_empty && !email_empty) {

        var data = [];
        console.log("Hola probando");
        $table.find("tbody tr").each(function () {
          var $selected = $(this).find("select[name='product']");
          var product_id = $selected.children(":selected").data("id");
          console.log("Product");
          console.log(product_id);
          var $quantity = $(this).find("input[name='quantity']");
          var qty = $quantity.val();

          var vals = {
            product_id: product_id,
            qty: qty,
          };
          data.push(vals);
        });

        var name = $name.val();
        var email = $email.val();
        //var partner_id = $partner_id.val();
        console.log(data);
        if (data.length > 0) {
          self.submit_quotation(data, "", "");
        }

        //}
      },

      submit_quotation: function (data, name, email) {
        console.log("helloooooooooooo");

        console.log("listo");

        var $selected = $(this).find("select[name='partner_website']");
        var partner = $selected.children(":selected").data("id");

        // console.log(".....");
        // console.log($selected.children(":selected"));
        // console.log($selected);
        // console.log(partner);
        // var partner = $selected.val();
        // console.log(partner);

        // var $partner_id = $(".partner_website");
        // console.log($partner_id);
        // var partner_id = $partner_id.val();
        // console.log(partner_id);

        const partner_website = document.querySelector("#partner_website");
        console.log(partner_website.value);

        var self = this;
        return self
          ._rpc({
            route: "/website_quick_quotation/submit_quotation_partner",
            params: {
              data: data,
              name: name,
              email: email,
              partner_id: partner_website.value,
            },
            args: [
              {
                partner_id: partner_website.value,
              },
            ],
          })
          .then(function (res) {
            var web_base_url = window.origin;
            if (res) {
              window.location = web_base_url + "/quick-quotation-thank-you";
            } else {
              window.location = web_base_url + "/quick-quotation-error";
            }
          });
      },

      on_search_prodcuts: function (e) {
        console.log("esto fue pa");
        e.preventDefault();
        var value = e.target.value.toLowerCase().trim();
        var $table = $(".table_quick_quotation");
        $table.find("tbody tr").each(function () {
          $(this)
            .find("td:eq(1)")
            .each(function () {
              var $selected = $(this).find("select[name='product']");
              var text = $selected.children(":selected").text();
              var id = text.toLowerCase().trim();
              var not_found = id.indexOf(value) == -1;
              $(this).closest("tr").toggle(!not_found);
              return not_found;
            });
        });
      },
    });
  }
);
