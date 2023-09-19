# -*- coding: utf-8 -*-

from odoo import fields,api,models,_

class InheritResConfigSetting(models.TransientModel):
    _inherit = 'res.config.settings'
    _description = 'backorder configuration'


    automatic_backorder = fields.Boolean('Backorde automatico',related="company_id.automatic_backorder",readonly=False)