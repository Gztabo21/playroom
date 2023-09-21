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

from odoo import fields, http, _
from odoo.http import request
from odoo.exceptions import AccessError, MissingError
from odoo.addons.website_quick_quotation.controllers.main import WebsiteQuickQuotation


class WebsiteQuickQuotationInherit(WebsiteQuickQuotation):
    @http.route("/quotation/quick",website=True,auth="public")
    def  index(self, **kw):
        data = request.env["res.partner"].get_data_products(1)
        clients = request.env["res.partner"].get_partners_all()
        return http.request.render('website_quick_quotation.quick_quotation', {
        'datos': data,
        'clients': clients,
    })

    @http.route("/website_quick_quotation/get_products_data",type="json",auth="public",website=True,)
    def get_products_data(self, **kw):
        #         <t t-set="combination" t-value="product._get_first_possible_combination()"/>
        # <t t-set="combination_info" t-value="product._get_combination_info(combination, add_qty=add_qty or 1, pricelist=pricelist)"/>
        print("Productos")
        print(self)
        print(kw)
        products = (
            request.env["product.product"]
            .sudo()
            .search_read(
                [],
                [
                    "name",
                    "id",
                    "uom_id",
                ],
            )
        )
        return products

    @http.route("/website_quick_quotation/load_products_data",type="json",auth="public",website=True,)
    def load_products_data(self, partner_id, **kw):
        data = request.env["res.partner"].get_data_products(partner_id)
        return data

    @http.route(
        "/website_quick_quotation/submit_quotation_partner",
        type="json",
        auth="public",
        website=True,
    )
    def submit_quotation_partner(self, data, name, email, partner_id: None, **kw):
        print("Estamos en la funcion")
        print(data)
        print(kw)
        print("sisas")
        print(partner_id)
        lines = []
        # if not name or not email or not data:
        #     return
        if not partner_id:
            return

        partner_sudo = request.env["res.partner"].sudo()
        sale_sudo = request.env["sale.order"].sudo()

        # partner = partner_sudo.search([("email", "=", email)], limit=1)
        partner = partner_sudo.search([("id", "=", partner_id)], limit=1)
        # if not partner:
        #     partner = partner_sudo.create(
        #         {
        #             "company_type": "person",
        #             "name": name,
        #             "email": email,
        #         }
        #     )

        for d in data:
            if d["product_id"] and d["qty"]:
                val = {
                    "product_id": d["product_id"],
                    "product_uom_qty": d["qty"],
                }
                lines.append((0, 0, val))

        vals = {
            "partner_id": partner.id,
            "order_line": lines,
        }
        sale_order = sale_sudo.create(vals)
        return sale_order.id
