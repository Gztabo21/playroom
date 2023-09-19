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


class SaleOrderInherit(models.Model):
    _inherit = "sale.order"

    @api.depends("order_line")
    def _compute_sale_order_taxes(self):

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
        "sale.order.tax",
        "order_id",
        string="Impuestos",
        compute="_compute_sale_order_taxes",
        store=True,
    )

    @api.depends("order_line.price_total")
    def _amount_all(self):
        """
        Compute the total amounts of the SO.
        """
        super(SaleOrderInherit, self)._amount_all()
        for order in self:
            amount_untaxed = amount_tax = 0.0

            amount_withholding = sum(
                x["amount"] for x in order.validate_amount_taxes_withholdings()
            )
            print(order.validate_amount_taxes_withholdings())
            print("amount_withholding" + str(amount_withholding))

            for line in order.order_line:
                amount_untaxed += line.price_subtotal
                amount_tax += line.price_tax

            if amount_withholding < 0:
                amount_tax += abs(amount_withholding)
            # else:
            #     amount_tax += -amount_withholding
            print(
                {
                    "amount_untaxed": amount_untaxed,
                    "amount_tax": amount_tax,
                    "amount_total": amount_untaxed + amount_tax,
                }
            )
            order.update(
                {
                    "amount_untaxed": amount_untaxed,
                    "amount_tax": amount_tax,
                    "amount_total": amount_untaxed + amount_tax,
                }
            )

    @api.depends(lambda self: self._get_compute_discount_total_depends())
    def _compute_discount_total(self):
        for order in self:
            discount_total = sum(order.order_line.mapped("discount_total"))
            price_total_no_discount = sum(
                order.order_line.mapped("price_total_no_discount")
            )
            amount_withholding = sum(
                x["amount"] for x in order.validate_amount_taxes_withholdings()
            )

            if amount_withholding < 0:
                price_total_no_discount += abs(amount_withholding)

            order.update(
                {
                    "discount_total": discount_total,
                    "price_total_no_discount": price_total_no_discount,
                }
            )

    def _create_invoices(self, grouped=False, final=False):
        move = super(SaleOrderInherit, self)._create_invoices(grouped, final)
        move._onchange_partner_id()
        if move.invoice_line_ids:
            for line in move.invoice_line_ids:
                line.sudo()._onchange_product_id()
                move.sudo()._onchange_invoice_line_ids()
                move.sudo().write({"invoice_line_ids": move.invoice_line_ids})
                move._onchange_invoice_line_ids()
        return move

    def return_data_taxes_order_line(self, order):
        tax_grouped = {}
        currency = order.currency_id or order.company_id.currency_id
        if order.order_line:
            for line in order.order_line:
                price_reduce = line.price_unit * (1.0 - line.discount / 100.0)
                taxes = line.tax_id.compute_all(
                    price_reduce,
                    quantity=line.product_uom_qty,
                    product=line.product_id,
                    partner=order.partner_shipping_id,
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
        # print("*****")
        # print(data_taxes)
        # print(data_withholdings)

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
                    tax_id = line.tax_id
                    if tax_id:
                        for tax in tax_id:
                            if tax.is_withholdings:
                                if tax.base_taxes_ids:
                                    for base in tax.base_taxes_ids:
                                        date_list = []
                                        print(base)
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
