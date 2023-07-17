# -*- coding: utf-8 -*-
##############################################################################
#
#    OpenERP, Open Source Management Solution
#    Copyright (C) Sitaram Solutions (<https://sitaramsolutions.in/>).
#
#    For Module Support : info@sitaramsolutions.in  or Skype : contact.hiren1188
#
##############################################################################
from odoo import api, models
import json

class ResUsers(models.Model):
    _inherit = "res.users"

    def get_access_rights(self):
        data = {}
        if self.user_has_groups('sr_user_access_rights_hide_buttons.group_hide_create'):
            data.update({'create': True})
        if self.user_has_groups('sr_user_access_rights_hide_buttons.group_hide_edit'):
            data.update({'edit': True})
        if self.user_has_groups('sr_user_access_rights_hide_buttons.group_hide_export'):
            data.update({'export': True})
        if self.user_has_groups('sr_user_access_rights_hide_buttons.group_hide_import'):
            data.update({'import': True})
        if self.user_has_groups('sr_user_access_rights_hide_buttons.group_hide_action_button'):
            data.update({'action': True})
        if self.user_has_groups('sr_user_access_rights_hide_buttons.group_hide_print'):
            data.update({'print': True})
        if self.user_has_groups('sr_user_access_rights_hide_buttons.group_hide_dublicate'):
            data.update({'duplicate': True})
        if self.user_has_groups('sr_user_access_rights_hide_buttons.group_hide_delete'):
            data.update({'delete': True})
        datas = json.dumps(data) if data else False
        return datas