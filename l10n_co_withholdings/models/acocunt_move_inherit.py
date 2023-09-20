#   coding: utf-8
##############################################################################
#
#   Copyright (C) 2021 Odoo Inc
#   Autor: Brayhan Andres Jaramillo Castaño
#   Correo: brayhanjaramillo@hotmail.com
#
#   You should have received a copy of the GNU Affero General Public License
#   along with this program.  If not, see <http://www.gnu.org/licenses/>.
#
##############################################################################
from unittest import result
from odoo import api, models, fields, _
from odoo.exceptions import RedirectWarning, UserError, ValidationError, AccessError
from datetime import datetime, timedelta
from collections import defaultdict
from odoo.tools.misc import formatLang


import logging

_logger = logging.getLogger(__name__)


class AccountMoveInherit(models.Model):
    _inherit = "account.move"

    @api.model
    def _get_default_invoice_date(self):
        default_date = fields.Date.context_today(self)
        if self._context.get("default_type", "entry") in self.get_purchase_types(
            include_receipts=True
        ):
            default_date = fields.Date.context_today(self)

        return default_date

    @api.depends("line_ids", "invoice_line_ids")
    def compute_account_move_tax(self):
        data_taxes = []

        for invoice in self:
            data_withholdings = self.return_data_taxes()

            for x in invoice.line_ids:

                tax_id = x.tax_line_id
                value_credit = x.credit
                value_debit = x.debit
                value_tax_base_amount = x.tax_base_amount

                values = {
                    "credit": value_credit,
                    "debit": value_debit,
                    "tax_base_amount": value_tax_base_amount,
                }
                if tax_id:

                    amount_total = 0
                    if x.debit != 0:
                        amount_total = x.debit
                    if x.credit != 0:
                        amount_total = x.credit

                    vals = {
                        "move_id": self.id,
                        "name": x.name,
                        "tax_id": tax_id.id,
                        "account_id": x.account_id.id,
                        "base": x.tax_base_amount,
                        "amount": amount_total,
                    }
                    if data_withholdings:
                        for taxes in data_withholdings:
                            if taxes["tax"] == tax_id.id:

                                if taxes["type_tax"] == "general":
                                    vals["base"] = invoice.amount_untaxed

                                    if vals["amount"] < 0:
                                        vals["amount"] = vals["base"] * (
                                            taxes["percent"] / 100
                                        )

                                    if vals["amount"] > 0:
                                        if taxes["percent"] < 0:
                                            vals["amount"] = (
                                                vals["base"] * (taxes["percent"] / 100)
                                            ) * -1
                                        else:
                                            vals["amount"] = vals["base"] * (
                                                taxes["percent"] / 100
                                            )

                                if taxes["type_tax"] == "line":
                                    if float(values["tax_base_amount"]) < float(
                                        taxes["base"]
                                    ) or invoice.amount_untaxed < float(taxes["base"]):
                                        vals["amount"] = 0
                    data_taxes.append((0, 0, vals))

            invoice.account_move_tax_ids = None
            invoice.account_move_tax_ids = data_taxes

    account_move_tax_ids = fields.One2many(
        "account.move.tax",
        "move_id",
        compute="compute_account_move_tax",
        string="Tax",
        store=True,
    )
    invoice_date = fields.Date(
        string="Invoice/Bill Date",
        required=True,
        readonly=True,
        index=True,
        copy=False,
        states={"draft": [("readonly", False)]},
        default=_get_default_invoice_date,
    )

    def calculate_holding(self):
        self._onchange_invoice_line_ids()

    @api.onchange("invoice_line_ids")
    def _onchange_invoice_line_ids(self):
        res = super(AccountMoveInherit, self)._onchange_invoice_line_ids()
        data_taxes = []
        sum_debit = 0
        sum_credit = 0
        data_line_ids = []
        for invoice in self:
            data_withholdings = self.return_data_taxes()
            invoice._onchange_recompute_dynamic_lines()
            for x in invoice.line_ids:

                tax_id = x.tax_line_id
                value_credit = x.credit
                value_debit = x.debit
                value_tax_base_amount = x.tax_base_amount

                values = {
                    "credit": value_credit,
                    "debit": value_debit,
                    "tax_base_amount": value_tax_base_amount,
                }

                if tax_id:

                    amount_total = 0
                    if x.debit != 0:
                        amount_total = x.debit
                    if x.credit != 0:
                        amount_total = x.credit

                    vals = {
                        "move_id": self.id,
                        "name": x.name,
                        "tax_id": tax_id.id,
                        "account_id": x.account_id.id,
                        "base": x.tax_base_amount,
                        "amount": amount_total,
                    }

                    if data_withholdings:
                        for taxes in data_withholdings:
                            if taxes["tax"] == tax_id.id:
                                if taxes["type_tax"] == "general":
                                    vals["base"] = invoice.amount_untaxed

                                    if vals["amount"] < 0:
                                        vals["amount"] = vals["base"] * (
                                            taxes["percent"] / 100
                                        )

                                    if vals["amount"] > 0:
                                        if taxes["percent"] < 0:
                                            vals["amount"] = (
                                                vals["base"] * (taxes["percent"] / 100)
                                            ) * -1
                                        else:
                                            vals["amount"] = vals["base"] * (
                                                taxes["percent"] / 100
                                            )

                                    if values["credit"] < 0:
                                        values["credit"] = (
                                            values["tax_base_amount"]
                                            * (taxes["percent"] / 100)
                                        ) * -1

                                    if values["credit"] > 0:
                                        values["credit"] = values["tax_base_amount"] * (
                                            taxes["percent"] / 100
                                        )

                                    if values["debit"] < 0:
                                        values["debit"] = (
                                            values["tax_base_amount"]
                                            * (taxes["percent"] / 100)
                                        ) * -1

                                    if values["debit"] > 0:
                                        values["debit"] = values["tax_base_amount"] * (
                                            taxes["percent"] / 100
                                        )

                                    values["tax_base_amount"] = (
                                        -(invoice.amount_untaxed)
                                        if values["tax_base_amount"] < 0
                                        else invoice.amount_untaxed
                                    )

                                    data_line_ids.append((1, x.id, values))

                            if taxes["type_tax"] == "line":
                                if taxes["tax"] == tax_id.id:
                                    if float(values["tax_base_amount"]) < float(
                                        taxes["base"]
                                    ) or invoice.amount_untaxed < float(taxes["base"]):
                                        vals["amount"] = 0
                                        update_value = {
                                            "credit": 0,
                                            "debit": 0,
                                            "tax_base_amount": value_tax_base_amount,
                                            "balance": 0,
                                            "price_unit": 0,
                                            "price_subtotal": 0,
                                            "price_total": 0,
                                        }
                                        sum_debit += x.debit
                                        sum_credit += x.credit
                                        data_line_ids.append((1, x.id, update_value))

            line_ids = []

            for item in invoice.line_ids:
                vals = {
                    "id": item._origin.id if item._origin else "",
                    "name": item.name,
                    "account_id": item.account_id.id,
                    # "base": item.tax_base_amount,
                    "balance": item.balance,
                    "debit": item.debit,
                    "credit": item.credit,
                }
                _logger.info(vals)
                line_ids.append(vals)
            _logger.info("*****")
            calculate_amount_main = 0
            data_calculate_main = {}
            if data_line_ids:
                _logger.info("-----")
                for item in line_ids:
                    if invoice.move_type in ["out_invoice", "out_refund"]:
                        if calculate_amount_main < item["debit"]:
                            calculate_amount_main = item["debit"]
                            data_calculate_main = item

                    if invoice.move_type in ["in_invoice", "in_refund"]:
                        if calculate_amount_main < item["credit"]:
                            calculate_amount_main = item["credit"]
                            data_calculate_main = item

                _logger.info(data_calculate_main)
                if data_calculate_main:

                    value_sum = 0
                    if invoice.move_type in ["in_invoice", "in_refund"]:
                        value_sum = sum_credit
                        data_calculate_main["credit"] = (
                            data_calculate_main["credit"] + sum_credit
                        )
                        data_calculate_main["balance"] = (
                            data_calculate_main["balance"] - value_sum
                        )

                    if invoice.move_type in ["out_invoice", "out_refund"]:

                        value_sum = sum_debit

                        data_calculate_main["debit"] = (
                            data_calculate_main["debit"] + sum_debit
                        )

                        data_calculate_main["balance"] = (
                            data_calculate_main["balance"] + value_sum
                        )
                    _logger.info(data_calculate_main)
                    if "id" in data_calculate_main:
                        if data_calculate_main["id"]:
                            data_line_ids.append(
                                (1, data_calculate_main["id"], data_calculate_main)
                            )

                invoice.line_ids = data_line_ids
            invoice._onchange_recompute_dynamic_lines()

    def return_data_taxes(self):
        """
        Permite retornar la data de retenciones con los impuestos que se configuraron
        se valida que los impuestos sean de tipo general y que esten activos, como tambien que se encuentren en el rango
        de la fecha de la factura
        """

        data_taxes = []
        sum_total = 0

        format_date = "%Y-%m-%d"

        def daterange(start_date, end_date):
            for n in range(int((end_date - start_date).days)):
                yield start_date + timedelta(n)

        for x in self:
            invoice_date = x.invoice_date
            base_amount = 0
            sum_total = x.amount_untaxed
            if x.line_ids:
                for line in x.line_ids:
                    tax_id = line.tax_line_id
                    if tax_id:
                        if tax_id.is_withholdings:
                            if tax_id.base_taxes_ids:
                                for base in tax_id.base_taxes_ids:
                                    date_list = []
                                    start_date = datetime.strptime(
                                        str(base.start_date), format_date
                                    )
                                    end_date = datetime.strptime(
                                        str(base.end_date), format_date
                                    )
                                    for single_date in daterange(start_date, end_date):
                                        date_list.append(
                                            str(single_date.strftime(format_date))
                                        )

                                    if str(invoice_date) in date_list:
                                        if base.is_active:
                                            base_amount = base.amount

                                        vals = {
                                            "tax": tax_id.id,
                                            "base": base_amount,
                                            "type_tax": base.type_tax,
                                            "percent": tax_id.amount,
                                        }
                                        if base_amount:
                                            if base.type_tax == "general":
                                                if sum_total >= base_amount:
                                                    data_taxes.append(vals)
                                            if base.type_tax == "line":
                                                data_taxes.append(vals)

        return data_taxes

    @api.depends(
        "line_ids.price_subtotal",
        "line_ids.tax_base_amount",
        "line_ids.tax_line_id",
        "partner_id",
        "currency_id",
    )
    def _compute_invoice_taxes_by_group(self):
        super(AccountMoveInherit, self)._compute_invoice_taxes_by_group()
        data_taxes = self.return_line_taxes_withholdings()
        for move in self:

            # Not working on something else than invoices.
            if not move.is_invoice(include_receipts=True):
                move.amount_by_group = []
                continue

            balance_multiplicator = -1 if move.is_inbound() else 1

            tax_lines = move.line_ids.filtered("tax_line_id")
            base_lines = move.line_ids.filtered("tax_ids")

            tax_group_mapping = defaultdict(
                lambda: {
                    "base_lines": set(),
                    "base_amount": 0.0,
                    "tax_amount": 0.0,
                }
            )

            # Compute base amounts.
            for base_line in base_lines:
                base_amount = balance_multiplicator * (
                    base_line.amount_currency
                    if base_line.currency_id
                    else base_line.balance
                )

                for tax in base_line.tax_ids.flatten_taxes_hierarchy():

                    if base_line.tax_line_id.tax_group_id == tax.tax_group_id:
                        continue

                    tax_group_vals = tax_group_mapping[tax.tax_group_id]
                    if base_line not in tax_group_vals["base_lines"]:
                        tax_group_vals["base_amount"] += base_amount
                        tax_group_vals["base_lines"].add(base_line)

            tax_amount = 0
            # Compute tax amounts.
            for tax_line in tax_lines:
                data_tax = list(
                    filter(
                        lambda item: item["tax_id"] == tax_line.tax_line_id.id,
                        data_taxes,
                    )
                )

                if not data_tax:
                    tax_amount = balance_multiplicator * (
                        tax_line.amount_currency
                        if tax_line.currency_id
                        else tax_line.balance
                    )
                else:
                    tax_amount = 0
                tax_group_vals = tax_group_mapping[tax_line.tax_line_id.tax_group_id]
                tax_group_vals["tax_amount"] += tax_amount

            tax_groups = sorted(tax_group_mapping.keys(), key=lambda x: x.sequence)
            amount_by_group = []
            for tax_group in tax_groups:
                tax_group_vals = tax_group_mapping[tax_group]
                amount_by_group.append(
                    (
                        tax_group.name,
                        tax_group_vals["tax_amount"],
                        tax_group_vals["base_amount"],
                        formatLang(
                            self.env,
                            tax_group_vals["tax_amount"],
                            currency_obj=move.currency_id,
                        ),
                        formatLang(
                            self.env,
                            tax_group_vals["base_amount"],
                            currency_obj=move.currency_id,
                        ),
                        len(tax_group_mapping),
                        tax_group.id,
                    )
                )

            move.amount_by_group = amount_by_group

    def return_line_taxes_withholdings(self):
        data_taxes = []
        for result_tax in self.account_move_tax_ids:
            if result_tax.tax_id.is_withholdings and result_tax.amount == 0:
                data_taxes.append(
                    {"tax_id": result_tax.tax_id.id, "amount": result_tax.amount}
                )

        #
        return data_taxes
