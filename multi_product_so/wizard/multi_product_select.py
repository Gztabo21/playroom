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
import time
from odoo import models, api, fields, _
from odoo.exceptions import UserError


class MultiProductSelect(models.TransientModel):
    _name = "multi.product.select"
    _description = "Multiple producto en Orden de Venta"

    product_ids = fields.Many2many(
        "product.product",
        "multi_product_select_order_rel",
        "wizard_id",
        "product_id",
        string="Productos",
    )

    def return_pricelist(self):
        context = self.env.context
        price_list_id = None
        if "pricelist" in context:
            price_list_id = self.env["product.pricelist"].search(
                [("id", "=", context.get("pricelist"))]
            )

        return price_list_id

    def return_data_product(self):
        data = []
        if self.product_ids:
            for product in self.product_ids:
                if product.product_qty_aux:

                    vals = {
                        "product_id": product.id,
                        "name": product.display_name,
                        "product_uom_qty": product.product_qty_aux,
                        "product_uom": product.uom_id.id,
                        "price_unit": product.price,
                    }
                    data.append((0, 0, vals))
        return data

    def load_order_line(self):
        context = self.env.context

        object_id = None
        if "sale_id" in context:
            object_id = [context["sale_id"]]
        if "purchase_id" in context:
            object_id = [context["purchase_id"]]

        if object_id:
            model = context.get("active_model", False)
            if model:
                model_object_id = self.env[model].browse(object_id)
                if model_object_id:
                    data = self.return_data_product()
                    model_object_id.sudo().write({"order_line": data})
                    product_ids = self.product_ids.ids
                    for line in model_object_id.order_line:
                        product = line.product_id
                        if product.id in product_ids:
                            line.product_id_change()
                            # line.product_uom_change()
                            line._onchange_discount()
