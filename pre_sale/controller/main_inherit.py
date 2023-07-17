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


from odoo import http
from odoo.http import request

from odoo import fields
from odoo.addons.website_save_cart.controllers.main import SaveCart


class SaveCartInherit(SaveCart):
    def create_save_cart(self, cart_name, order, lines):
        vals = {
            "name": cart_name,
            "sale_order_id": order.id,
            "partner_id": request.env.user.partner_id.id,
            "cart_lines": lines,
        }
        is_pre_sale = request.env["sale.order"].sudo().validate_pre_sale()
        if is_pre_sale:
            order.sudo().write({"pre_sale": True})
        return vals

    def create_lines_cart(self, save_cart_lines, line):
        save_cart_lines.append(
            (
                0,
                0,
                {
                    "product_id": line.product_id.id,
                    "product_uom_qty": line.product_uom_qty,
                    "product_uom": line.product_uom.id,
                    "price_unit": line.price_unit,
                },
            )
        )

    @http.route(
        ["/shop/multicart/add"],
        type="http",
        auth="user",
        methods=["POST", "GET"],
        website=True,
    )
    def add_multicart(self, **kw):
        order = request.website.sale_get_order()
        if kw.get("cart_name") and order:
            if order.state in ["draft", "sent"]:
                save_cart_lines = []
                if order.order_line:
                    for line in order.order_line:
                        self.create_lines_cart(save_cart_lines, line)

                vals_create = self.create_save_cart(
                    kw.get("cart_name"), order, save_cart_lines
                )
                request.env["save.cart"].sudo().create(vals_create)

        return request.redirect(request.httprequest.referrer)
