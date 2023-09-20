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

from odoo import SUPERUSER_ID, _, api, fields, models
from odoo.exceptions import AccessError, MissingError, UserError, ValidationError
from odoo.addons.stock.models.stock_move import PROCUREMENT_PRIORITIES
from odoo.tools import DEFAULT_SERVER_DATETIME_FORMAT
from odoo.tools.float_utils import float_compare, float_is_zero

import logging

_logger = logging.getLogger(__name__)


class StockPickingInherit(models.Model):
    _inherit = "stock.picking"

    def update_value_initial_final(
        self, model_config_parameter, get_value_initial, get_value_final, sum_value
    ):
        value_initial = model_config_parameter.search([("key", "=", "value_initial")])
        if value_initial:
            value_initial.write({"value": str(get_value_initial + sum_value)})

        value_final = model_config_parameter.search([("key", "=", "value_final")])
        if value_final:
            value_final.write({"value": str(get_value_final + sum_value)})

    def search_stock_valuation_layer_old(self):
        """
        Permite buscar todos los registros que no tienen el movimiento de inventario
        """
        domain = [
            ("company_id", "=", self.env.company.id),
            ("account_move_id", "=", False),
            ("stock_move_id", "!=", False),
        ]

        sql = """
            SELECT svl.id AS id
            FROM stock_valuation_layer svl, stock_move sm
            WHERE svl.stock_move_id = sm.id
            AND svl.account_move_id is null
            AND sm.purchase_line_id is null
            AND svl.company_id = %s
        """ % (
            self.env.company.id
        )
        self.env.cr.execute(sql)
        res = self.env.cr.dictfetchall()
        data = []
        for record in res:
            data.append(record.get("id"))
        # domain = [("id", "in", [18414, 18415])]
        domain = [("id", "in", data)]
        valuation_layer_ids = (
            self.env["stock.valuation.layer"].sudo().search(domain, order="id asc")
        )

        valuation_layer_ids = valuation_layer_ids.filtered(
            lambda svl: svl.product_id.valuation == "real_time"
        )
        _logger.info("*****")
        _logger.info(
            {"id": valuation_layer_ids[0].id, "size": len(valuation_layer_ids)}
        )

        return valuation_layer_ids

    def calculate_cost_old(self, initial: int = 0, final: int = 0):

        valuation_layer_ids = self.search_stock_valuation_layer_old()
        sum_value = 500

        # model_config_parameter = (
        #     self.env["ir.config_parameter"].sudo().with_company(self.env.company.id)
        # )

        # get_value_initial = int(
        #     model_config_parameter.with_company(self.env.company.id).get_param(
        #         "value_initial"
        #     )
        # )

        # get_value_final = int(
        #     model_config_parameter.with_company(self.env.company.id).get_param(
        #         "value_final"
        #     )
        # )

        try:
            if valuation_layer_ids:
                if final == 0:
                    final = len(valuation_layer_ids)

                # initial = get_value_initial
                # final = get_value_final
                for iterator in range(initial, final):
                    svl = valuation_layer_ids[iterator]

                    cost_old = 0

                    product_id = svl.product_id
                    account_id = (
                        svl.product_id.categ_id.property_account_expense_categ_id
                    )

                    vals = {
                        "iterator": iterator,
                        "svl": svl.id,
                        "stock_move_id": svl.stock_move_id.id,
                    }
                    _logger.info(vals)

                    if svl.stock_move_id:
                        order = svl.stock_move_id.origin
                        invoice_id = self.env["account.move"].search(
                            [("invoice_origin", "=", order)]
                        )
                        if invoice_id:
                            invoice_line_ids = invoice_id.line_ids
                            if invoice_line_ids:
                                for line in invoice_line_ids:
                                    product_invoice_id = line.product_id
                                    if (
                                        product_id.id == product_invoice_id.id
                                        and account_id.id == line.account_id.id
                                    ):
                                        cost_old = line.debit
                        svl.unit_cost = cost_old / svl.quantity
                        svl.value = cost_old

                        if not svl.product_id.valuation == "real_time":
                            _logger.info("Entro")
                            continue
                        # if svl.currency_id.is_zero(svl.value):
                        #     continue

                        svl.stock_move_id._account_entry_movee(
                            svl.quantity,
                            svl.description + " [*]",
                            svl.id,
                            svl.value,
                            svl.create_date.date(),
                        )
                    # svl.account_move_id.date = svl.create_date.date()
                # self.update_value_initial_final(
                #     model_config_parameter,
                #     get_value_initial,
                #     get_value_final,
                #     sum_value,
                # )

        except (AccessError, MissingError, MemoryError, KeyError):
            _logger.info("Error")
            # self.update_value_initial_final(
            #     model_config_parameter,
            #     get_value_initial,
            #     get_value_final,
            #     sum_value,
            # )

    def calculate_cost_old_button(self):

        valuation_layer_ids = self.search_stock_valuation_layer_old()

        initial = 0
        final = 100

        try:
            if valuation_layer_ids:
                if final == 0:
                    final = len(valuation_layer_ids)

                for iterator in range(initial, final):
                    svl = valuation_layer_ids[iterator]

                    cost_old = 0

                    product_id = svl.product_id
                    account_id = (
                        svl.product_id.categ_id.property_account_expense_categ_id
                    )

                    vals = {
                        "iterator": iterator,
                        "svl": svl.id,
                        "stock_move_id": svl.stock_move_id.id,
                    }
                    _logger.info(vals)

                    if svl.stock_move_id:
                        order = svl.stock_move_id.origin
                        invoice_id = self.env["account.move"].search(
                            [("invoice_origin", "=", order)]
                        )
                        if invoice_id:
                            invoice_line_ids = invoice_id.line_ids
                            if invoice_line_ids:
                                for line in invoice_line_ids:
                                    product_invoice_id = line.product_id
                                    if (
                                        product_id.id == product_invoice_id.id
                                        and account_id.id == line.account_id.id
                                    ):
                                        cost_old = line.debit
                        svl.unit_cost = cost_old / svl.quantity
                        svl.value = cost_old

                        if not svl.product_id.valuation == "real_time":
                            _logger.info("Entro")
                            continue
                        # if svl.currency_id.is_zero(svl.value):
                        #     continue

                        svl.stock_move_id._account_entry_movee(
                            svl.quantity,
                            svl.description + " [*]",
                            svl.id,
                            svl.value,
                            svl.create_date.date(),
                        )

        except (AccessError, MissingError, MemoryError, KeyError):
            _logger.info("Error")

    def calculate_product_cost_old(self):

        scraps = self.env["stock.scrap"].search([("picking_id", "=", self.id)])
        domain = [
            (
                "id",
                "in",
                (self.move_lines + scraps.move_id).stock_valuation_layer_ids.ids,
            )
        ]
        print(domain)
        valuation_layer_ids = self.env["stock.valuation.layer"].sudo().search(domain)

        for svl in valuation_layer_ids:
            product_id = svl.product_id

        # creando el asiento contable
        for svl in valuation_layer_ids:
            print(not svl.product_id.valuation == "real_time")
            print(svl.product_id.valuation)
            print(svl.currency_id.is_zero(svl.value))
            if not svl.product_id.valuation == "real_time":
                continue
            # if svl.currency_id.is_zero(svl.value):
            #     continue
            print("estsamos por aca en el _action_done")
            svl.stock_move_id._account_entry_move(
                svl.quantity, svl.description, svl.id, svl.value
            )

        # action = self.env["ir.actions.actions"]._for_xml_id(
        #     "stock_account.stock_valuation_layer_action"
        # )
        # context = literal_eval(action["context"])
        # context.update(self.env.context)
        # context["no_at_date"] = True
        # return dict(action, domain=domain, context=context)

    def button_validate_atlas(self):
        # Clean-up the context key at validation to avoid forcing the creation of immediate
        # transfers.

        ctx = dict(self.env.context)
        ctx.pop("default_immediate_transfer", None)
        self = self.with_context(ctx)

        # Sanity checks.
        pickings_without_moves = self.browse()
        pickings_without_quantities = self.browse()
        pickings_without_lots = self.browse()
        products_without_lots = self.env["product.product"]

        for picking in self:
            if not picking.move_lines and not picking.move_line_ids:
                pickings_without_moves |= picking

            picking.message_subscribe([self.env.user.partner_id.id])
            picking_type = picking.picking_type_id
            precision_digits = self.env["decimal.precision"].precision_get(
                "Product Unit of Measure"
            )
            no_quantities_done = all(
                float_is_zero(move_line.qty_done, precision_digits=precision_digits)
                for move_line in picking.move_line_ids.filtered(
                    lambda m: m.state not in ("done", "cancel")
                )
            )
            no_reserved_quantities = all(
                float_is_zero(
                    move_line.product_qty,
                    precision_rounding=move_line.product_uom_id.rounding,
                )
                for move_line in picking.move_line_ids
            )
            if no_reserved_quantities and no_quantities_done:
                pickings_without_quantities |= picking

            if picking_type.use_create_lots or picking_type.use_existing_lots:
                lines_to_check = picking.move_line_ids
                if not no_quantities_done:
                    lines_to_check = lines_to_check.filtered(
                        lambda line: float_compare(
                            line.qty_done,
                            0,
                            precision_rounding=line.product_uom_id.rounding,
                        )
                    )
                for line in lines_to_check:
                    product = line.product_id
                    if product and product.tracking != "none":
                        if not line.lot_name and not line.lot_id:
                            pickings_without_lots |= picking
                            products_without_lots |= product

        if not self._should_show_transfers():
            if pickings_without_moves:
                raise UserError(_("Please add some items to move."))
            if pickings_without_quantities:
                raise UserError(self._get_without_quantities_error_message())
            if pickings_without_lots:
                raise UserError(
                    _("You need to supply a Lot/Serial number for products %s.")
                    % ", ".join(products_without_lots.mapped("display_name"))
                )
        else:
            message = ""
            if pickings_without_moves:
                message += _(
                    "Transfers %s: Please add some items to move."
                ) % ", ".join(pickings_without_moves.mapped("name"))
            if pickings_without_quantities:
                message += _(
                    "\n\nTransfers %s: You cannot validate these transfers if no quantities are reserved nor done. To force these transfers, switch in edit more and encode the done quantities."
                ) % ", ".join(pickings_without_quantities.mapped("name"))
            if pickings_without_lots:
                message += _(
                    "\n\nTransfers %s: You need to supply a Lot/Serial number for products %s."
                ) % (
                    ", ".join(pickings_without_lots.mapped("name")),
                    ", ".join(products_without_lots.mapped("display_name")),
                )
            if message:
                raise UserError(message.lstrip())

        # Run the pre-validation wizards. Processing a pre-validation wizard should work on the
        # moves and/or the context and never call `_action_done`.
        if not self.env.context.get("button_validate_picking_ids"):
            self = self.with_context(button_validate_picking_ids=self.ids)
        # res = self._pre_action_done_hook()
        # if res is not True:
        #    return res

        # Call `_action_done`.

        if self.env.context.get("picking_ids_not_to_backorder"):
            pickings_not_to_backorder = self.browse(
                self.env.context["picking_ids_not_to_backorder"]
            )
            pickings_to_backorder = self - pickings_not_to_backorder
        else:
            pickings_not_to_backorder = self.env["stock.picking"]
            pickings_to_backorder = self
        pickings_not_to_backorder.with_context(cancel_backorder=True)._action_done()
        pickings_to_backorder.with_context(cancel_backorder=False)._action_done()

        return True
