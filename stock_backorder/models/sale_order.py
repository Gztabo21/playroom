# -*- coding: utf-8 -*-


from odoo import fields,api,models,_ 


class SaleOrderInherit(models.Model):
    _inherit = 'sale.order'
    _description = 'sale.order backorder'


    def _action_confirm(self):
        res = super(SaleOrderInherit, self)._action_confirm()
        if self.env.company.automatic_backorder:
            self._backorder_automatic()
        return res
    def _backorder_automatic(self):
        # agrego la cantidad terminada
        for move_line_id in self.picking_ids.move_line_ids_without_package:
            move_line_id.qty_done = move_line_id.product_uom_qty
        # validar stock picking
        self.picking_ids.button_validate()
