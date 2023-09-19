#   coding: utf-8
##############################################################################
#
#   Copyright (C) 2022 Odoo Inc
#   Autor: Brayhan Andres Jaramillo Castaño
#   Correo: brayhanjaramillo@hotmail.com
#
#   You should have received a copy of the GNU Affero General Public License
#   along with this program.  If not, see <http://www.gnu.org/licenses/>.
#
##############################################################################

from odoo import fields, models, api
from typing import Dict
from itertools import groupby


class SaveCartInherit(models.Model):
    _inherit = "save.cart"

    def data_product(self, save_cart_ids) -> Dict[str, any]:
        """
        Retorna la data de las carritos guardados
        """
        data = []
        for cart in save_cart_ids:
            if cart.cart_lines:
                for line_cart in cart.cart_lines:
                    vals = {
                        "product": line_cart.product_id.id,
                        "product_uom_qty": line_cart.product_uom_qty,
                        "price_unit": line_cart.price_unit,
                        "product_uom": line_cart.product_uom.id,
                    }
                    data.append(vals)
        return data

    def merge_data(self, data) -> Dict[str, any]:
        """
        Agrupa los productos encontrados en los carritos
        """

        def key_func(k):
            return k["product"]

        data = sorted(data, key=key_func)
        data_complete = []
        for key, value in groupby(data, key_func):
            vals = {"product": key, "data": list(value), "product_uom_qty": 0}
            data_complete.append(vals)

        for item in data_complete:
            item["product_uom_qty"] = sum([x["product_uom_qty"] for x in item["data"]])

        return data_complete

    def return_data_line(self, data):
        data_line = []
        for record in data:
            print(record)
            vals = {
                "product": 1,
                "data": [{"product": 1, "product_uom_qty": 1.0, "product_uom": False}],
                "product_uom_qty": 1.0,
            }
            if record["data"]:
                price_unit = record["data"][0]["price_unit"]
                vals = {
                    "product_id": record["product"],
                    "product_uom_qty": record["product_uom_qty"],
                    "price_unit": price_unit,
                }
                data_line.append((0, 0, vals))
        return data_line

    @api.model
    def union_save_carts(self, save_cart_ids):
        print("Entrando en esta funcion")
        print(save_cart_ids)

        result = False

        try:
            save_cart_ids = save_cart_ids.replace("save.cart", "")
            save_cart_ids = eval(save_cart_ids)

            save_cart_ids = (
                self.env["save.cart"]
                .sudo()
                .search([("id", "in", [x for x in save_cart_ids])])
            )
            print(save_cart_ids)
            if save_cart_ids:
                data_product = self.data_product(save_cart_ids)
                data_merge = self.merge_data(data_product)
                print(data_merge)
                # data_merge = [
                #     {
                #         "product": 1,
                #         "data": [
                #             {
                #                 "product": 1,
                #                 "product_uom_qty": 1.0,
                #                 "price_unit": 2000000.0,
                #                 "product_uom": 1,
                #             }
                #         ],
                #         "product_uom_qty": 1.0,
                #     },
                #     {
                #         "product": 3,
                #         "data": [
                #             {
                #                 "product": 3,
                #                 "product_uom_qty": 1.0,
                #                 "price_unit": 2000000.0,
                #                 "product_uom": 1,
                #             },
                #             {
                #                 "product": 3,
                #                 "product_uom_qty": 2.0,
                #                 "price_unit": 2000000.0,
                #                 "product_uom": 1,
                #             },
                #         ],
                #         "product_uom_qty": 3.0,
                #     },
                #     {
                #         "product": 4,
                #         "data": [
                #             {
                #                 "product": 4,
                #                 "product_uom_qty": 1.0,
                #                 "price_unit": 1000000.0,
                #                 "product_uom": 1,
                #             }
                #         ],
                #         "product_uom_qty": 1.0,
                #     },
                # ]
                iterator = 1
                data_line = self.return_data_line(data_merge)
                print(data_line)
                if data_merge:
                    for record in save_cart_ids:
                        if iterator == 1:
                            order_id = record.sale_order_id
                            if order_id:
                                order_id.update_presale()
                            record.cart_lines = None
                            record.cart_lines = data_line
                        else:
                            record.sudo().unlink()
                        iterator += 1
                result = True
        except:
            result = False
        return result
