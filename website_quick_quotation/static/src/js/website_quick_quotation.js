odoo.define('website_quick_quotation.quick_quotation', function (require) {
    "use strict";

    var core = require('web.core');
    var publicWidget = require('web.public.widget');
    var rpc = require('web.rpc');
    var _t = core._t;

    publicWidget.registry.quick_quotation = publicWidget.Widget.extend({
        selector: '#wrapwrap:has(.o_quick_quotation)',
        events: {
            "click .add-new": _.debounce(function (e) {
                this.add_new_row(e);
            }, 200, true),

            "click .add": _.debounce(function (e) {
                this.add_row(e);
            }, 200, true),

            "click .edit": _.debounce(function (e) {
                this.edit_row(e);
            }, 200, true),

            "click .delete": _.debounce(function (e) {
                this.delete_row(e);
            }, 200, true),

            "change select#product": _.debounce(function (e) {
                this.on_change_product(e);
            }, 200, true),

            "change .quantity": _.debounce(function (e) {
                this.on_change_quantity(e);
            }, 200, true),

            "click .submit": _.debounce(function (e) {
                this.on_click_submit(e);
            }, 200, true),

            "keyup .search_prodcuts" : "on_search_prodcuts",
        },

        willStart: function () {
            var self = this;
            var def = this._super.apply(this, arguments);
            var def1 = this._rpc({
                route: '/website_quick_quotation/get_products_data',                
            }).then(function (res) {
                self.products = res;
            })            
            return Promise.all([def, def1]);
        },

        init: function (parent, options) {
            this._super.apply(this, arguments);
        },

        start: function () {
            var self = this;            
            return this._super.apply(this, arguments).then(function () {
                $('.submit').attr("disabled", "disabled");
                $('.search_prodcuts').attr("disabled", "disabled");
            })
        },

        add_new_row: function(e){      
            e.preventDefault();
            e.stopPropagation();
            var $target = $(e.currentTarget);     
            $target.attr("disabled", "disabled");
            var index = $("table tbody tr:last-child").index();            
            this.actions = '<a class="add" title="Add" data-toggle="tooltip">' +
                '<i class="fa fa-check"></i>' + 
                '</a>' +
                '<a class="edit" title="Edit" data-toggle="tooltip">' +
                '<i class="fa fa-edit"></i>' +
                '</a>' +
                '<a class="delete" title="Delete" data-toggle="tooltip">' +
                '<i class="fa fa-trash"></i>' + 
                '</a>';            

            var row = "";
            row += '<tr>';
            row += '<td></td>';
            row += '<td><select type="text" class="form-control product" name="product" id="product">';
            row +='<option></option>';
            for (let i = 0; i < this.products.length; i++) {                
                row += '<option  data-id="' + this.products[i]['id'] + '" data-unit="'+ this.products[i]['uom_id'] +'">'+ this.products[i]['name'] +'</option>';
            }
            row += '</select></td>';
            row += '<td><span class="unit" name="unit" id="unit"></span></td>';
            row += '<td><input type="text" class="form-control quantity" name="quantity" id="quantity"></td>';
            row += '<td>' + this.actions + '</td>';
            row += '</tr>';

            $("table").append(row);		
            $("table tbody tr").eq(index + 1).find(".add, .edit").toggle();

            this.add_row_number($('#table_quick_quotation'));

            $('#table_quick_quotation').find('select').each(function(){
                if (!$(this).data('select2'))
                {                        
                    $(this).select2({
                        width: '100%',
                        placeholder: "Select Product",
                        allowClear: true
                    });
                }                
            });
            
            this.check_row_number($('#table_quick_quotation'));
        },

        add_row_number:function($table) {
            var count = 0;
            $table.find("tbody tr").each(function(index, el) {
              $(el).find("td:eq(0)").html(++count + ".");
            });
        },

        check_row_number: function($table){
            var count = 0;
            $table.find("tbody tr").each(function(index, el) {
                count = count + 1;
            });
            if(count > 0){
                $('.submit').removeAttr("disabled");
                $('.search_prodcuts').removeAttr("disabled");
            }else{
                $('.submit').attr("disabled", "disabled");
                $('.search_prodcuts').attr("disabled", "disabled");
            }
        },  

        delete_row_number: function(e){
            e.preventDefault();
            var $target = $(e.currentTarget);
            var $row = $target.parents("tr");
            if ($row) {
                $row.remove();
                this.add_row_number($("#table_quick_quotation"));
            }
            this.check_row_number($('#table_quick_quotation'));
        },

        add_row: function(e){
            e.preventDefault();
            e.stopPropagation();
            var select_empty = false;
            var input_empty = false;

            var $target = $(e.currentTarget);     
            var $select = $target.parents("tr").find('select');
            var $input = $target.parents("tr").find('input');
            
            $select.each(function(){
                if(!$(this).val()){
                    $(this).addClass("error");
                    select_empty = true;
                } else{
                    $(this).removeClass("error");
                    select_empty = false;
                }
            });

            $input.each(function(){
                if(!$(this).val()){
                    $(this).addClass("error");
                    input_empty = true;
                } else{
                    $(this).removeClass("error");
                    input_empty = false;
                }
            });
            $target.parents("tr").find(".error").first().focus();

            if(!select_empty && !input_empty){
                $target.parents("tr").find("select").each(function(){
                    if ($(this).getAttributes()['id'] == 'product'){
                        $(this).attr("disabled", "disabled");
                    }
                    
                });
                $target.parents("tr").find("input").each(function(){
                    if ($(this).getAttributes()['id'] == 'quantity'){
                        $(this).attr("disabled", "disabled");
                    }
                });

                $target.parents("tr").find(".add, .edit").toggle();
                $(".add-new").removeAttr("disabled");
            }
        },

        edit_row: function(e){
            e.preventDefault();
            e.stopPropagation();
            var $target = $(e.currentTarget);
            
            $target.parents("tr").find("select").each(function(){                
                if ($(this).getAttributes()['id'] == 'product'){
                    $(this).removeAttr("disabled", "disabled");
                }
            });
            $target.parents("tr").find("input").each(function(){                
                if ($(this).getAttributes()['id'] == 'quantity'){
                    $(this).removeAttr("disabled", "disabled");
                }
            });

            $target.parents("tr").find(".add, .edit").toggle();
            $(".add-new").attr("disabled", "disabled");
        },

        delete_row: function(e){
            e.preventDefault();
            e.stopPropagation();
            var $target = $(e.currentTarget);
            $target.parents("tr").remove();            
		    $(".add-new").removeAttr("disabled");

            this.delete_row_number(e);
        },

        on_change_product: function(e){
            e.preventDefault();
            e.stopPropagation();            
            var $target = $(e.currentTarget);
            var $select = $target.parents("tr").find("select[name='product']");
            var $unit = $target.parents("tr").find("span[name='unit']");
            var unit = $select.children(":selected").data("unit");     
    
            if(unit != null){                                              
                $unit[0].innerHTML  = unit.split(',')[1];
            }else{
                $unit[0].innerHTML  = '';
            }
        },

        on_change_quantity: function(e){
            e.preventDefault();
            e.stopPropagation();
            var $target = $(e.currentTarget);
            var quantity = $target.val();
            if (isNaN(quantity)){
                $target.val('');
            }
        },

        on_click_submit: function(e){
            e.preventDefault();
            e.stopPropagation();

            var self = this;
            
            var name_empty = false;
            var email_empty = false;

            var select_empty = false;
            var input_empty = false;


            var $name = $('.input_name');
            var $email = $('.input_email');

            if ($name){
                if(!$name.val()){
                    $name.addClass("error");
                    name_empty = true;
                } else{
                    $name.removeClass("error");
                    name_empty = false;
                }
            }

            if ($email){
                if(!$email.val()){
                    $email.addClass("error");
                    email_empty = true;
                } else{
                    $email.removeClass("error");
                    email_empty = false;
                }
            }

            var $table = $('.table_quick_quotation');
            var $select = $table.find("tr").find('select');
            var $input = $table.find("tr").find('input');
            
            $select.each(function(){
                if(!$(this).val()){
                    $(this).addClass("error");
                    select_empty = true;
                } else{
                    $(this).removeClass("error");
                    select_empty = false;
                }
            });

            $input.each(function(){
                if(!$(this).val()){
                    $(this).addClass("error");
                    input_empty = true;
                } else{
                    $(this).removeClass("error");
                    input_empty = false;
                }
            });

            if(!select_empty && !input_empty && !name_empty && !email_empty){
                var data = [];

                $table.find("tbody tr").each(function(){
                    var $selected = $(this).find("select[name='product']");
                    var product_id = $selected.children(":selected").data("id");
                    
                    var $quantity = $(this).find("input[name='quantity']");
                    var qty = $quantity.val();
                    
                    var vals = {
                        'product_id': product_id,
                        'qty': qty,
                    }
                    data.push(vals);                    
                });
               
                var name = $name.val();
                var email = $email.val();

                if (data.length > 0){
                    self.submit_quotation(data, name, email);
                }
            }            
        },

        submit_quotation: function (data, name, email) {            
            var self = this;
            return self._rpc({
                route: '/website_quick_quotation/submit_quotation',
                params: {
                    'data' : data,
                    'name' : name,
                    'email': email,
                }
            }).then(function (res) {                
                var web_base_url = window.origin;
                if (res) {                    
                    window.location = web_base_url + '/quick-quotation-thank-you';
                } else {
                    window.location = web_base_url+ '/quick-quotation-error'
                }
            })
        },

        on_search_prodcuts: function(e){
            e.preventDefault();
            var value = e.target.value.toLowerCase().trim();
            var $table = $('.table_quick_quotation');
            $table.find("tbody tr").each(function () {
                $(this).find("td:eq(1)").each(function () {
                    var $selected = $(this).find("select[name='product']");
                    var text = $selected.children(":selected").text();             
                    var id = text.toLowerCase().trim();
                    var not_found = (id.indexOf(value) == -1);
                    $(this).closest('tr').toggle(!not_found);
                    return not_found;
                });
            });
        }

    });
})