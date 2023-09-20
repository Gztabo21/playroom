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
from itertools import groupby


import logging

_logger = logging.getLogger(__name__)


class SaleOrderLineInherit(models.Model):
    _inherit = "sale.order.line"

    @api.onchange("product_id", "product_uom_qty")
    def onchange_product_verificate_qty(self):
        for record in self:
            if record.product_id:
                product_id = record.product_id
                # if product_id.free_qty == 0:
                # _logger.info("Producto")
                # _logger.info(product_id.free_qty)
                # _logger.info(product_id.outgoing_qty)
                # _logger.info(product_id.incoming_qty)
                # _logger.info(product_id.virtual_available)
                if product_id.outgoing_qty < 0 or product_id.free_qty <= 0:
                    name_product = product_id.name

                    if product_id.free_qty > 0:
                        record.product_uom_qty = product_id.free_qty
                    else:
                        record.product_id = False
                        raise ValidationError(
                            "El producto %s no posee unidades disponibles para la venta."
                            % (name_product)
                        )
                else:
                    if record.product_uom_qty > product_id.free_qty:
                        record.product_uom_qty = product_id.free_qty


class StockMoveInherit(models.Model):
    _inherit = "stock.move"

    def _generate_valuation_lines_dataa(
        self,
        partner_id,
        qty,
        debit_value,
        credit_value,
        debit_account_id,
        credit_account_id,
        description,
    ):
        # This method returns a dictionary to provide an easy extension hook to modify the valuation lines (see purchase for an example)
        self.ensure_one()
        debit_line_vals = {
            "name": description,
            "product_id": self.product_id.id,
            "quantity": qty,
            "product_uom_id": self.product_id.uom_id.id,
            "ref": description,
            "partner_id": partner_id,
            "debit": -debit_value if debit_value < 0 else 0,
            "credit": debit_value if debit_value > 0 else 0,
            "account_id": debit_account_id,
        }

        credit_line_vals = {
            "name": description,
            "product_id": self.product_id.id,
            "quantity": qty,
            "product_uom_id": self.product_id.uom_id.id,
            "ref": description,
            "partner_id": partner_id,
            "credit": -credit_value if credit_value < 0 else 0,
            "debit": credit_value if credit_value > 0 else 0,
            "account_id": credit_account_id,
        }

        rslt = {
            "credit_line_vals": credit_line_vals,
            "debit_line_vals": debit_line_vals,
        }
        if credit_value != debit_value:
            # for supplier returns of product in average costing method, in anglo saxon mode
            diff_amount = debit_value - credit_value
            price_diff_account = (
                self.product_id.property_account_creditor_price_difference
            )

            if not price_diff_account:
                price_diff_account = (
                    self.product_id.categ_id.property_account_creditor_price_difference_categ
                )
            if not price_diff_account:
                raise UserError(
                    _(
                        "Configuration error. Please configure the price difference account on the product or its category to process this operation."
                    )
                )

            rslt["price_diff_line_vals"] = {
                "name": self.name,
                "product_id": self.product_id.id,
                "quantity": qty,
                "product_uom_id": self.product_id.uom_id.id,
                "ref": description,
                "partner_id": partner_id,
                "credit": diff_amount < 0 and -diff_amount or 0,
                "debit": diff_amount > 0 and diff_amount or 0,
                "account_id": price_diff_account.id,
            }
        return rslt

    def _prepare_account_move_linee(
        self, qty, cost, credit_account_id, debit_account_id, description
    ):
        """
        Generate the account.move.line values to post to track the stock valuation difference due to the
        processing of the given quant.
        """
        self.ensure_one()

        # the standard_price of the product may be in another decimal precision, or not compatible with the coinage of
        # the company currency... so we need to use round() before creating the accounting entries.
        debit_value = self.company_id.currency_id.round(cost)
        credit_value = debit_value

        valuation_partner_id = self._get_partner_id_for_valuation_lines()
        res = [
            (0, 0, line_vals)
            for line_vals in self._generate_valuation_lines_dataa(
                valuation_partner_id,
                qty,
                debit_value,
                credit_value,
                debit_account_id,
                credit_account_id,
                description,
            ).values()
        ]

        return res

    def _create_account_move_linee(
        self,
        credit_account_id,
        debit_account_id,
        journal_id,
        qty,
        description,
        svl_id,
        cost,
        date,
    ):
        self.ensure_one()
        AccountMove = self.env["account.move"].with_context(
            default_journal_id=journal_id
        )

        move_lines = self._prepare_account_move_linee(
            qty, cost, credit_account_id, debit_account_id, description
        )
        if move_lines:
            new_account_move = AccountMove.sudo().create(
                {
                    "journal_id": journal_id,
                    "line_ids": move_lines,
                    "date": date,
                    "ref": description,
                    "stock_move_id": self.id,
                    "stock_valuation_layer_ids": [(6, None, [svl_id])],
                    "move_type": "entry",
                }
            )

            new_account_move._post()

    def _account_entry_movee(self, qty, description, svl_id, cost, date):
        """Accounting Valuation Entries"""
        _logger.info("_account_entry_movee")
        self.ensure_one()
        if self.product_id.type != "product":
            # no stock valuation for consumable products
            _logger.info(
                "self.product_id.type != product: %s"
                % (str(self.product_id.type != "product"))
            )
            # return False
        if self.restrict_partner_id:
            # if the move isn't owned by the company, we don't make any valuation
            _logger.info(
                "self.restrict_partner_id: %s" % (str(self.restrict_partner_id))
            )
            # return False

        company_from = (
            self._is_out()
            and self.mapped("move_line_ids.location_id.company_id")
            or False
        )
        company_to = (
            self._is_in()
            and self.mapped("move_line_ids.location_dest_id.company_id")
            or False
        )

        (
            journal_id,
            acc_src,
            acc_dest,
            acc_valuation,
        ) = self._get_accounting_data_for_valuation()
        # Create Journal Entry for products arriving in the company; in case of routes making the link between several
        # warehouse of the same company, the transit location belongs to this company, so we don't need to create accounting entries

        if self._is_in():
            if self._is_returned(valued_type="in"):
                self.with_company(company_to)._create_account_move_linee(
                    acc_dest,
                    acc_valuation,
                    journal_id,
                    qty,
                    description,
                    svl_id,
                    cost,
                    date,
                )
            else:
                self.with_company(company_to)._create_account_move_linee(
                    acc_src,
                    acc_valuation,
                    journal_id,
                    qty,
                    description,
                    svl_id,
                    cost,
                    date,
                )

        # Create Journal Entry for products leaving the company
        if self._is_out() or True:  # se valida con true para forzarlo a entrar
            cost = -1 * cost
            _logger.info("self._is_out() or True")
            if self._is_returned(valued_type="out"):
                _logger.info("self._is_returned(valued_type='out')")
                self.with_company(company_from)._create_account_move_linee(
                    acc_valuation,
                    acc_src,
                    journal_id,
                    qty,
                    description,
                    svl_id,
                    cost,
                    date,
                )
            else:
                _logger.info("1 else")
                self.with_company(company_from)._create_account_move_linee(
                    acc_valuation,
                    acc_dest,
                    journal_id,
                    qty,
                    description,
                    svl_id,
                    cost,
                    date,
                )

        if self.company_id.anglo_saxon_accounting:
            # Creates an account entry from stock_input to stock_output on a dropship move. https://github.com/odoo/odoo/issues/12687
            _logger.info("self.company_id.anglo_saxon_accounting primero")
            if self._is_dropshipped():
                _logger.info("self._is_dropshipped()")
                if cost > 0:
                    _logger.info("1 if")
                    self.with_company(self.company_id)._create_account_move_linee(
                        acc_src,
                        acc_valuation,
                        journal_id,
                        qty,
                        description,
                        svl_id,
                        cost,
                        date,
                    )
                else:
                    _logger.info("self.company_id.anglo_saxon_accounting else")
                    cost = -1 * cost
                    self.with_company(self.company_id)._create_account_move_linee(
                        acc_valuation,
                        acc_dest,
                        journal_id,
                        qty,
                        description,
                        svl_id,
                        cost,
                        date,
                    )
            elif self._is_dropshipped_returned():
                _logger.info("self._is_dropshipped_returned()")
                if cost > 0:
                    _logger.info("2 if")
                    self.with_company(self.company_id)._create_account_move_linee(
                        acc_valuation,
                        acc_src,
                        journal_id,
                        qty,
                        description,
                        svl_id,
                        cost,
                        date,
                    )
                else:
                    _logger.info("self._is_dropshipped_returned() else")
                    cost = -1 * cost
                    self.with_company(self.company_id)._create_account_move_linee(
                        acc_dest,
                        acc_valuation,
                        journal_id,
                        qty,
                        description,
                        svl_id,
                        cost,
                        date,
                    )

        if self.company_id.anglo_saxon_accounting:
            _logger.info("self.company_id.anglo_saxon_accounting 2")
            # Eventually reconcile together the invoice and valuation accounting entries on the stock interim accounts
            self._get_related_invoices()._stock_account_anglo_saxon_reconcile_valuation(
                product=self.product_id
            )

    def test(self):
        return self._action_done(cancel_backorder=True)

    def _create_dropshipped_svll(self, forced_quantity=None):
        """Create a `stock.valuation.layer` from `self`.

        :param forced_quantity: under some circunstances, the quantity to value is different than
            the initial demand of the move (Default value = None)
        """
        svl_vals_list = []
        for move in self:
            move = move.with_company(move.company_id)
            valued_move_lines = move.move_line_ids
            valued_quantity = 0
            for valued_move_line in valued_move_lines:
                valued_quantity += valued_move_line.product_uom_id._compute_quantity(
                    valued_move_line.qty_done, move.product_id.uom_id
                )
            quantity = forced_quantity or valued_quantity

            unit_cost = move._get_price_unit()
            print("unit cost")
            print(unit_cost)
            if move.product_id.cost_method == "standard":
                unit_cost = move.product_id.standard_price

            common_vals = dict(move._prepare_common_svl_vals(), remaining_qty=0)

            # create the in
            in_vals = {
                "unit_cost": unit_cost,
                "value": unit_cost * quantity,
                "quantity": quantity,
            }
            in_vals.update(common_vals)
            svl_vals_list.append(in_vals)

            # create the out
            out_vals = {
                "unit_cost": unit_cost,
                "value": unit_cost * quantity * -1,
                "quantity": quantity * -1,
            }
            out_vals.update(common_vals)
            svl_vals_list.append(out_vals)

        return (
            self.env["stock.valuation.layer"]
            .sudo()
            .search([("stock_move_id", "=", self.id)])
            .write(out_vals)
        )

    def action_donee(self):
        # # # Init a dict that will group the moves by valuation type, according to `move._is_valued_type`.
        # valued_moves = {valued_type: self.env['stock.move'] for valued_type in self._get_valued_types()}
        # for move in self:
        #     if float_is_zero(move.quantity_done, precision_rounding=move.product_uom.rounding):
        #         continue
        #     for valued_type in self._get_valued_types():
        #         if getattr(move, '_is_%s' % valued_type)():
        #             valued_moves[valued_type] |= move

        # # AVCO application
        # valued_moves['in'].product_price_update_before_done()
        # print('paso aca')
        # res = super(StockMove, self)._action_done(cancel_backorder=cancel_backorder)
        # print('pasando derecho')
        # # '_action_done' might have created an extra move to be valued
        # for move in res - self:
        #     for valued_type in self._get_valued_types():
        #         if getattr(move, '_is_%s' % valued_type)():
        #             valued_moves[valued_type] |= move

        self._create_dropshipped_svll()

        stock_valuation_layers = (
            self.env["stock.valuation.layer"]
            .sudo()
            .search([("stock_move_id", "=", self.id)])
        )

        # # Create the valuation layers in batch by calling `moves._create_valued_type_svl`.
        # for valued_type in self._get_valued_types():
        #     todo_valued_moves = valued_moves[valued_type]
        #     if todo_valued_moves:
        #         todo_valued_moves._sanity_check_for_valuation()
        #         stock_valuation_layers |= getattr(todo_valued_moves, '_create_%s_svl' % valued_type)()

        print(stock_valuation_layers)
        for svl in stock_valuation_layers:
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

        stock_valuation_layers._check_company()

        # # For every in move, run the vacuum for the linked product.
        # products_to_vacuum = valued_moves['in'].mapped('product_id')
        # company = valued_moves['in'].mapped('company_id') and valued_moves['in'].mapped('company_id')[0] or self.env.company
        # for product_to_vacuum in products_to_vacuum:
        #     product_to_vacuum._run_fifo_vacuum(company)

        # return res
