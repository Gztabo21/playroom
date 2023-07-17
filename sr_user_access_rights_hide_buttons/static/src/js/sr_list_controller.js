odoo.define('sr_user_access_rights_hide_buttons.ListController', function (require) {
"use strict";

/**
 * The List Controller controls the list renderer and the list model.  Its role
 * is to allow these two components to communicate properly, and also, to render
 * and bind all extra buttons/pager in the control panel.
 */

var core = require('web.core');
var BasicController = require('web.BasicController');
var DataExport = require('web.DataExport');
var Dialog = require('web.Dialog');
var ListConfirmDialog = require('web.ListConfirmDialog');
var session = require('web.session');
const viewUtils = require('web.viewUtils');
var session = require('web.session');
var ListController = require('web.ListController');

var _t = core._t;
var qweb = core.qweb;

ListController.include({
    events: _.extend({}, ListController.prototype.events, {
        'click .o_favorite_menu': '_onFilterCLick',
        'click .o_dropdown': '_onActionMenuClick',
    }),
    /**
     * Display and bind all buttons in the control panel
     *
     * Note: clicking on the "Save" button does nothing special. Indeed, all
     * editable rows are saved once left and clicking on the "Save" button does
     * induce the leaving of the current row.
     *
     * @override
     */
    renderButtons: function ($node) {
        if (this.noLeaf || !this.hasButtons) {
            this.hasButtons = false;
            this.$buttons = $('<div>');
        } else {
            this.$buttons = $(qweb.render(this.buttons_template, {widget: this}));
            this.$buttons.on('click', '.o_list_button_add', this._onCreateRecord.bind(this));
            this._assignCreateKeyboardBehavior(this.$buttons.find('.o_list_button_add'));
            this.$buttons.find('.o_list_button_add').tooltip({
                delay: {show: 200, hide: 0},
                title: function () {
                    return qweb.render('CreateButton.tooltip');
                },
                trigger: 'manual',
            });
            this.$buttons.on('mousedown', '.o_list_button_discard', this._onDiscardMousedown.bind(this));
            this.$buttons.on('click', '.o_list_button_discard', this._onDiscard.bind(this));
        }
        if ($node) {
            this.$buttons.appendTo($node);
        }
        var buttons = this.$buttons
        this._rpc({
            model: "res.users",
            method: 'get_access_rights',
            args: [session.user_context.uid]
        }).then(function(data){
            var vals = JSON.parse(data)
            if(vals){
                if (vals['create']){
                    buttons.find('.o_list_button_add').addClass('d-none');
                } else {
                    buttons.find('.o_list_button_add').removeClass('d-none');
                }
                if (vals['export']){
                    buttons.find('.o_button_upload_bill').addClass('d-none');
                    buttons.find('.o_list_export_xlsx').addClass('d-none');
                } else {
                    buttons.find('.o_button_upload_bill').removeClass('d-none');
                    buttons.find('.o_list_export_xlsx').removeClass('d-none');
                }
                if (vals['import']){
                    $('.o_favorite_menu').find('.o_import_menu').addClass('d-none')
                } else {
                    $('.o_favorite_menu').find('.o_import_menu').removeClass('d-none')
                }
            }
        })
    },

    _onFilterCLick: function(events){
        this._rpc({
            model: "res.users",
            method: 'get_access_rights',
            args: [session.user_context.uid]
        }).then(function(data){
            var vals = JSON.parse(data)
            if(vals){
                if (vals['import']){
                    $('.o_import_menu').addClass('d-none')
                } else {
                    $('.o_import_menu').removeClass('d-none')
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
                if (vals['export']){
                    $('.dropdown-menu').find('li:contains("Export")').addClass('d-none')
                } else {
                    $('.dropdown-menu').find('li:contains("Export")').removeClass('d-none')
                }
            }
        })
    },
});

});
