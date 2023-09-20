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
from odoo import models, _, api, fields
from datetime import datetime, timedelta
from odoo.exceptions import UserError
from odoo.tools.float_utils import float_is_zero
from itertools import groupby


class PurchaseOrderInherit(models.Model):
    _inherit = "purchase.order"

    @api.depends("order_line")
    def _compute_purchase_order_taxes(self):

        data = []

        for order in self:
            for tax in self.return_data_taxes_order_line(order).values():

                vals = {
                    "sequence": tax["sequence"],
                    "name": tax["name"],
                    "account_id": tax["account_id"],
                    "base": tax["base"],
                    "amount": tax["amount"],
                }
                data.append((0, 0, vals))
            order.taxes_ids = None
            order.taxes_ids = data

    taxes_ids = fields.One2many(
        "purchase.order.tax",
        "purchase_id",
        string="Impuestos",
        compute="_compute_purchase_order_taxes",
        store=True,
    )

    @api.depends("order_line.price_total")
    def _amount_all(self):
        """
        Compute the total amounts of the SO.
        """
        super(PurchaseOrderInherit, self)._amount_all()
        for order in self:

            print("*****")
            print(order.validate_amount_taxes_withholdings())
            amount_withholding = sum(
                (x["amount"]) for x in order.validate_amount_taxes_withholdings()
            )
            print(amount_withholding)

            amount_untaxed = amount_tax = 0.0
            for line in order.order_line:
                line._compute_amount()
                amount_untaxed += line.price_subtotal
                amount_tax += line.price_tax
            currency = (
                order.currency_id
                or order.partner_id.property_purchase_currency_id
                or self.env.company.currency_id
            )

            if amount_withholding < 0:
                amount_tax += abs(amount_withholding)

            order.update(
                {
                    "amount_untaxed": currency.round(amount_untaxed),
                    "amount_tax": currency.round(amount_tax),
                    "amount_total": amount_untaxed + amount_tax,
                }
            )

    def action_view_invoice(self, invoices=False):
        """This function returns an action that display existing vendor bills of
        given purchase order ids. When only one found, show the vendor bill
        immediately.
        """

        if not invoices:
            # Invoice_ids may be filtered depending on the user. To ensure we get all
            # invoices related to the purchase order, we read them in sudo to fill the
            # cache.
            self.sudo()._read(["invoice_ids"])
            invoices = self.invoice_ids

        for move in invoices:
            move._onchange_partner_id()
            if move.invoice_line_ids:
                move.sudo()._onchange_invoice_line_ids()
                # for line in move.invoice_line_ids:
                # line.sudo()._onchange_product_id()
                # move.sudo()._onchange_invoice_line_ids()
                # move.sudo().write({"invoice_line_ids": move.invoice_line_ids})
                # move._onchange_invoice_line_ids()

        result = self.env["ir.actions.act_window"]._for_xml_id(
            "account.action_move_in_invoice_type"
        )
        # choose the view_mode accordingly
        if len(invoices) > 1:
            result["domain"] = [("id", "in", invoices.ids)]
        elif len(invoices) == 1:
            res = self.env.ref("account.view_move_form", False)
            form_view = [(res and res.id or False, "form")]
            if "views" in result:
                result["views"] = form_view + [
                    (state, view) for state, view in result["views"] if view != "form"
                ]
            else:
                result["views"] = form_view
            result["res_id"] = invoices.id
        else:
            result = {"type": "ir.actions.act_window_close"}

        return result

    def return_data_taxes_order_line(self, order):
        tax_grouped = {}
        currency = order.currency_id or order.company_id.currency_id
        if order.order_line:
            for line in order.order_line:

                # line_order = line.with_company(line.company_id)
                # fpos = (
                #     line_order.order_id.fiscal_position_id
                #     or line_order.order_id.fiscal_position_id.get_fiscal_position(
                #         line_order.order_id.partner_id.id
                #     )
                # )

                # # filter taxes by company
                # taxes = line_order.product_id.supplier_taxes_id.filtered(
                #     lambda r: r.company_id == line_order.env.company
                # )
                # taxes_ids = fpos.map_tax(
                #     taxes, line_order.product_id, line_order.order_id.partner_id
                # )

                taxes = line.taxes_id.compute_all(
                    line.price_unit,
                    quantity=line.product_uom_qty,
                    product=line.product_id,
                    partner=order.partner_id,
                )["taxes"]

                for tax in taxes:
                    val = {
                        "order": self._origin.id,
                        "account_id": tax["account_id"],
                        "name": tax["name"],
                        "amount": tax["amount"],
                        "base": currency.round(tax["base"]),
                        "sequence": tax["sequence"],
                    }

                    key = val["name"]
                    if key not in tax_grouped:
                        tax_grouped[key] = val
                    else:
                        tax_grouped[key]["base"] += val["base"]
                        tax_grouped[key]["amount"] += val["amount"]

            for t in tax_grouped.values():
                t["base"] = currency.round(t["base"])
                t["amount"] = currency.round(t["amount"])

        return tax_grouped

    def validate_amount_taxes_withholdings(self):
        data_taxes = self.return_data_taxes_order_line(self).values()
        data_withholdings = self.return_data_taxes()
        data = []

        for withholdings_tax in data_withholdings:
            tax = list(
                filter(
                    lambda index: index["name"] == withholdings_tax["name"], data_taxes
                )
            )[0]
            if tax:
                if withholdings_tax["type_tax"] == "general":
                    if tax["base"] < withholdings_tax["base"]:
                        data.append(tax)
                if withholdings_tax["type_tax"] == "line":
                    if tax["base"] < withholdings_tax["base"]:
                        data.append(tax)

        return data

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

        data_tax_ids = []
        for x in self:
            date_order = x.date_order
            base_amount = 0
            sum_total = x.amount_untaxed
            if x.order_line:
                for line in x.order_line:
                    tax_id = line.taxes_id
                    if tax_id:
                        for tax in tax_id:
                            if tax.is_withholdings:
                                if tax.base_taxes_ids:
                                    for base in tax.base_taxes_ids:
                                        date_list = []
                                        start_date = datetime.strptime(
                                            str(base.start_date), format_date
                                        )
                                        end_date = datetime.strptime(
                                            str(base.end_date), format_date
                                        )

                                        for single_date in daterange(
                                            start_date, end_date
                                        ):
                                            date_list.append(
                                                str(single_date.strftime(format_date))
                                            )
                                        if str(date_order.date()) in date_list:
                                            if base.is_active:
                                                base_amount = base.amount

                                            if tax._origin.id not in data_tax_ids:
                                                vals = {
                                                    "tax": tax._origin.id,
                                                    "name": tax.name,
                                                    "base": base_amount,
                                                    "type_tax": base.type_tax,
                                                    "percent": tax.amount,
                                                }
                                                if base_amount:
                                                    if base.type_tax == "general":
                                                        if sum_total >= base_amount:
                                                            data_taxes.append(vals)
                                                    if base.type_tax == "line":
                                                        data_taxes.append(vals)
                                                    data_tax_ids.append(tax._origin.id)

        return data_taxes
