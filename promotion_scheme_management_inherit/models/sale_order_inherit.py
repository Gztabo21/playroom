# -*- coding: utf-8 -*-
##############################################################################
#
#    OpenERP, Open Source Management Solution
#    Copyright (C) 2004-2010 Tiny SPRL (<http://tiny.be>).
#
#    This program is free software: you can redistribute it and/or modify
#    it under the terms of the GNU Affero General Public License as
#    published by the Free Software Foundation, either version 3 of the
#    License, or (at your option) any later version.
#
#    This program is distributed in the hope that it will be useful,
#    but WITHOUT ANY WARRANTY; without even the implied warranty of
#    MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE.  See the
#    GNU Affero General Public License for more details.
#
#    Autor: Brayhan Andres Jaramillo Castaño
#    Correo: brayhanjaramillo@hotmail.com
#
#    You should have received a copy of the GNU Affero General Public License
#    along with this program.  If not, see <http://www.gnu.org/licenses/>.
#
##############################################################################

from odoo import api, fields, models, _
from datetime import datetime


class SaleOrderInherit(models.Model):
    _inherit = "sale.order"

    def create_scheme_data(self, promotion_product_id, line):
        for promotion_line in promotion_product_id.promotion_line_ids:
            qty_to_reward = line.product_uom_qty / promotion_product_id.product_qty
            reward_qty = int(qty_to_reward) * promotion_line.reward_product_qty
            vals = {
                "product_id": line.product_id.id,
                "reward_product_id": promotion_line.reward_product_id.id,
                "product_uom_id": promotion_line.reward_product_uom_id.id,
                "reward_qty": reward_qty,
                "sale_line_id": line.id,
                "sale_order_id": line.order_id.id,
            }
            exist_rewarded_product_ids = self.sale_reward_product_ids.filtered(
                lambda x: x.sale_line_id.id == line.id
                and x.reward_product_id.id == promotion_line.reward_product_id.id
            )
            for reward_line in exist_rewarded_product_ids:
                new_reward_line = [(1, reward_line.id, vals)]
                self.sale_reward_product_ids = new_reward_line
            if not exist_rewarded_product_ids:
                self.sale_reward_product_ids = [(0, 0, vals)]
