odoo.define('sr_user_access_rights_hide_buttons.ActionMenus', function (require) {
    "use strict";

    const ActionMenus = require('web.ActionMenus');
    const { patch } = require('web.utils');
    var session = require('web.session');
    const rpc = require('web.rpc');

    patch(ActionMenus, 'sr_user_access_rights_hide_buttons/static/src/js/action_menus.js', {
        async _setActionItems(props) {
            const result = this._super(...arguments)
            const has_action_access = await session.user_has_group('sr_user_access_rights_hide_buttons.group_hide_action_button');
            if(has_action_access){
                return [];
            }
            return result
        },
        async _setPrintItems(props) {
            const result = this._super(...arguments)
            const has_print_access = await session.user_has_group('sr_user_access_rights_hide_buttons.group_hide_print');
            if(has_print_access){
                return [];
            }
            return result
        },
    });
});