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


class ProductTemplateInherit(models.Model):
    _inherit = "product.template"

    def _compute_promotional_product_qty(self):
        for record in self:
            qty = len(record.search_promotional_product_qty())
            record.promotional_product_qty = qty
            record.promotional_product_description = "P" if qty > 0 else ""

    promotional_product_qty = fields.Integer(
        string="Promo", compute="_compute_promotional_product_qty"
    )
    promotional_product_description = fields.Char(
        string="Promo", compute="_compute_promotional_product_qty"
    )

    def return_domain_promotional_domain(self):
        for record in self:
            model_product = record.env["product.product"]
            product_id = model_product.search(
                [("product_tmpl_id", "=", record.id)], limit=1
            )
            if product_id:
                return [("reward_product_id", "=", product_id.id)]

            return []

    def return_sale_order_id(self):
        for record in self:
            context = record.env.context
            sale_order_id = context.get("sale_order_id", False)
            if sale_order_id:
                sale_order_id = (
                    record.env["sale.order"]
                    .sudo()
                    .search([("id", "=", int(sale_order_id))])
                )
            return sale_order_id

    def return_date_order(self):
        for record in self:
            context = record.env.context
            date_order = context.get("date_sale_order", False)
            if date_order:
                date_order = datetime.strptime(date_order, "%Y-%m-%d %H:%M:%S")
            return date_order

    def search_promotional_product_qty(self):
        for record in self:
            model_promotional_line = record.env["promotion.scheme.line"].sudo()
            product_promotional_line = []
            if record.id:
                product_promotional_line = model_promotional_line.search(
                    record.return_domain_promotional_domain()
                )

                date_order = record.return_date_order()
                if date_order:

                    product_promotional_line = product_promotional_line.filtered(
                        lambda r: r.promotion_id.start_date and r.promotion_id.end_date
                    )

                    product_promotional_line = product_promotional_line.filtered(
                        lambda r: r.promotion_id.start_date <= date_order.date()
                        and r.promotion_id.end_date >= date_order.date()
                    )

            return product_promotional_line

    def return_domain_promotional(self):
        for record in self:
            promotional_line_ids = record.search_promotional_product_qty()
            product_promotional_ids = []
            if promotional_line_ids:
                product_promotional_ids = [
                    item.promotion_id.id for item in promotional_line_ids
                ]
            print(product_promotional_ids)
            return product_promotional_ids

    def get_promotional_product(self):
        for record in self:

            return {
                "type": "ir.actions.act_window",
                "name": "Productos Promocionales",
                "view_mode": "tree,form",
                "res_model": "promotion.scheme",
                "domain": [("id", "in", record.return_domain_promotional())],
                "context": "{'create': False}",
            }
