from odoo import api, fields, models
from datetime import date


class SaleOrder(models.Model):
    _inherit = 'sale.order'

    sale_reward_product_ids = fields.One2many('sale.order.reward.products',
                                              'sale_order_id',
                                              string='Rewarded Products')

    def create_scheme_data(self, promotion_product_id, line):
        for promotion_line in promotion_product_id.promotion_line_ids:
            qty_to_reward = line.product_uom_qty / promotion_product_id.product_qty
            reward_qty = qty_to_reward * promotion_line.reward_product_qty
            vals = {
                'product_id': line.product_id.id,
                'reward_product_id': promotion_line.reward_product_id.id,
                'product_uom_id': promotion_line.reward_product_uom_id.id,
                'reward_qty': int(reward_qty),
                'sale_line_id': line.id,
                'sale_order_id': line.order_id.id
            }
            exist_rewarded_product_ids = self.sale_reward_product_ids.filtered(
                lambda
                x: x.sale_line_id.id == line.id and x.reward_product_id.id == promotion_line.reward_product_id.id)
            for reward_line in exist_rewarded_product_ids:
                new_reward_line = [(1, reward_line.id, vals)]
                self.sale_reward_product_ids = new_reward_line
            if not exist_rewarded_product_ids:
                self.sale_reward_product_ids = [(0, 0, vals)]

    def get_scheme_data(self):
        for line in self.order_line.filtered(lambda x: not x.is_reward_line):
            promotion_product_ids = self.env['promotion.scheme'].search(
                ['|', ('product_id', '=', line.product_id.id),
                 ('product_category_id', '=', line.product_id.categ_id.id),
                 ('product_qty', '<=', line.product_uom_qty)
                 ])
            for promotion_product_id in promotion_product_ids:
                if promotion_product_id.start_date:
                    if (promotion_product_id.start_date <= self.date_order.date()) and (
                            promotion_product_id.end_date >= self.date_order.date()):
                        self.create_scheme_data(promotion_product_id, line)
                    else:
                        continue
                else:
                    self.create_scheme_data(promotion_product_id, line)


class SaleOrderLine(models.Model):
    _inherit = 'sale.order.line'

    is_reward_line = fields.Boolean('Reward Line')


class SaleOrderRewardProducts(models.Model):
    _name = 'sale.order.reward.products'
    _description = 'Sale Order Reward Products'

    sale_order_id = fields.Many2one('sale.order', string='Sale Order')
    sale_line_id = fields.Many2one('sale.order.line', string='Sale Order Line')
    reward_product_id = fields.Many2one('product.product',
                                        string='Reward Product')
    product_id = fields.Many2one('product.product', string='Product')
    product_uom_id = fields.Many2one('uom.uom', string='Unit of measure')
    reward_qty = fields.Float('Quantity')

    @api.model_create_multi
    def create(self, vals_list):
        res = super(SaleOrderRewardProducts, self).create(vals_list=vals_list)
        for vals in vals_list:
            line_vals = {
                'product_id': res.reward_product_id.id,
                'name': 'Reward Product - ' + res.reward_product_id.name,
                'product_uom_qty': res.reward_qty,
                'product_uom': res.product_uom_id.id,
                'price_unit': 0.0,
                'order_id': res.sale_order_id.id,
                'is_reward_line': True,
                'sequence': 50
            }
            existing_sale_line_ids = self.env['sale.order.line'].search(
                [('order_id', '=', res.sale_order_id.id),
                 ('is_reward_line', '=', True),
                 ('product_id', '=', res.reward_product_id.id)])
            for sale_line in existing_sale_line_ids:
                sale_line.product_uom_qty += res.reward_qty
            if not existing_sale_line_ids:
                self.env['sale.order.line'].create(line_vals)

        return res

    def write(self, vals):
        res = super(SaleOrderRewardProducts, self).write(vals)
        for line in self:
            if 'reward_qty' in vals:
                existing_sale_line_id = self.env['sale.order.line'].search(
                    [('is_reward_line', '=', True),
                     ('product_id', '=', line.reward_product_id.id),
                     ('order_id', '=', line.sale_order_id.id)])
                reward_line_qty = self.env[
                    'sale.order.reward.products'].search(
                    [('sale_order_id', '=', line.sale_order_id.id),
                     ('reward_product_id', '=',
                      line.reward_product_id.id)]).mapped('reward_qty')
                existing_sale_line_id.product_uom_qty = sum(reward_line_qty)
        return res
