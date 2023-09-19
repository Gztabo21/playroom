# -*- coding: utf-8 -*-

from odoo import models, fields, _


class SaleOrder(models.Model):
    _inherit = "sale.order"

    is_seller = fields.Boolean('Is seller?')
    seller_partner_id = fields.Many2one('res.partner', 'Partner')