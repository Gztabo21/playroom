odoo.define('sr_user_access_rights_hide_buttons.FormController', function (require) {
"use strict";

var BasicController = require('web.BasicController');
var core = require('web.core');
var Dialog = require('web.Dialog');
var dialogs = require('web.view_dialogs');
var FormController = require("web.FormController");
var session = require('web.session');

var _t = core._t;
var qweb = core.qweb;

FormController.include({
    events: _.extend({}, FormController.prototype.events, {
        'click .o_dropdown': '_onActionMenuClick',
    }),

    updateButtons: function () {
        if (!this.$buttons) {
            return;
        }
        if (this.footerToButtons) {
            var $footer = this.renderer.$el && this.renderer.$('footer');
            if ($footer && $footer.length) {
                this.$buttons.empty().append($footer);
            }
        }
        var edit_mode = (this.mode === 'edit');
        this.$buttons.find('.o_form_buttons_edit')
            .toggleClass('o_hidden', !edit_mode);
        this.$buttons.find('.o_form_buttons_view')
            .toggleClass('o_hidden', edit_mode);
        var buttons = this.$buttons
        this._rpc({
            model: "res.users",
            method: 'get_access_rights',
            args: [session.user_context.uid]
        }).then(function(data){
            var vals = JSON.parse(data)
            if(vals){
                if (vals['create']){
                    buttons.find('.o_form_button_create').addClass('d-none');
                } else {
                    buttons.find('.o_form_button_create').removeClass('d-none');
                }
                if (vals['edit']){
                    buttons.find('.o_form_button_edit').addClass('d-none');
                } else {
                    buttons.find('.o_form_button_edit').removeClass('d-none');
                }
                if (vals['action']){
                    $($('.o_action_manager').find('.o_dropdown')).find('span:contains("Action")').parent().addClass('d-none')
                } else {
                    $($('.o_action_manager').find('.o_dropdown')).find('span:contains("Action")').parent().removeClass('d-none')
                }
                if (vals['print']){
                    $($('.o_action_manager').find('.o_dropdown')).find('span:contains("Print")').parent().addClass('d-none')
                } else {
                    $($('.o_action_manager').find('.o_dropdown')).find('span:contains("Print")').parent().removeClass('d-none')
                }
            }
        })
    },

    _onActionMenuClick: function(events){
        this._rpc({
            model: "res.users",
            method: 'get_access_rights',
            args: [session.user_context.uid]
        }).then(function(data){
            var vals = JSON.parse(data)
            if(vals){
                if (vals['duplicate']){
                    $('.dropdown-menu').find('li:contains("Duplicate")').addClass('d-none')
                } else {
                    $('.dropdown-menu').find('li:contains("Duplicate")').removeClass('d-none')
                }
                if (vals['delete']){
                    $('.dropdown-menu').find('li:contains("Delete")').addClass('d-none')
                } else {
                    $('.dropdown-menu').find('li:contains("Delete")').removeClass('d-none')
                }
            }
        })
    },
});
});
