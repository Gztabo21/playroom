# -*- coding: utf-8 -*-

from odoo import models, fields, api


class stock_backorder(models.Model):
    _inherit = 'res.company'
    _description = 'stock_backorder'


    automatic_backorder = fields.Boolean('Backorde automatico', default=False)