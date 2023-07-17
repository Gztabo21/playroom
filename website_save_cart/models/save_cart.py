# -*- coding: utf-8 -*-

from odoo import models, fields, api
from odoo.addons import decimal_precision as dp


class SaveCartLine(models.Model):
    _name = 'save.cart.line'
    _description = "Save Cart line"

    @api.depends('product_uom_qty', 'price_unit')
    def _compute_amount(self):
        for line in self:
            price = line.price_unit * line.product_uom_qty
            line.update({
                'price_subtotal': price,
            })

    save_cart_id = fields.Many2one('save.cart', string='Cart')
    product_id = fields.Many2one('product.product', string='Product', domain=[('sale_ok', '=', True)], change_default=True, ondelete='restrict', required=True)
    product_uom_qty = fields.Float(string='Quantity', digits='Product Unit of Measure', required=True, default=1.0)
    product_uom = fields.Many2one('uom.uom', string='Unit of Measure')
    product_image = fields.Binary('Product Image', related="product_id.image_1920", store=False)
    price_unit = fields.Float('Unit Price', required=True, digits='Product Price', default=0.0)
    price_subtotal = fields.Float(compute='_compute_amount', string='Subtotal', readonly=True, store=True)
    company_id = fields.Many2one('res.company', string='Company', required=True, default=lambda self: self.env.user.company_id)

    @api.onchange('product_id',  'product_uom_qty')
    def product_change(self):
        if not self.product_uom_qty or not self.product_id:
            self.price_unit = 0.0
            return
        else:
            self.price_unit = self.product_id.with_context(pricelist=self.env['product.pricelist'].search([], limit=1).id).price


class SaveCart(models.Model):
    _name = 'save.cart'
    _description = "Save Cart"

    @api.depends('cart_lines.price_subtotal')
    def _amount_all(self):
        for order in self:
            amount_total = 0.0
            for line in order.cart_lines:
                amount_total += line.price_subtotal
            order.update({
                'amount_total': amount_total,
            })

    name = fields.Char(string='Name', required=True)
    partner_id = fields.Many2one("res.partner", string="Partner")
    cart_lines = fields.One2many('save.cart.line', 'save_cart_id', string='Cart Lines', copy=True, auto_join=True)
    date_order = fields.Datetime(string='Create Date', required=True, readonly=True, index=True, copy=False, default=fields.Datetime.now)
    amount_total = fields.Float(string='Total', store=True, readonly=True, compute='_amount_all', track_visibility='always')
    sale_order_id = fields.Many2one("sale.order", string="Sale Order")
    company_id = fields.Many2one('res.company', string='Company', required=True, default=lambda self: self.env.user.company_id)
