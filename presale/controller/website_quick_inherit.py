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
from odoo.addons.website_quick_quotation_inherit.controllers.main_inherit import (
    WebsiteQuickQuotationInherit,
)


class WebsiteQuotationInherit(WebsiteQuickQuotationInherit):
    @http.route(
        "/website_quick_quotation/submit_quotation_partner",
        type="json",
        auth="public",
        website=True,
    )
    def submit_quotation_partner(self, data, name, email, partner_id: None, **kw):
        lines = []

        if not partner_id:
            return

        partner_sudo = request.env["res.partner"].sudo()
        sale_sudo = request.env["sale.order"].sudo()

        partner = partner_sudo.search([("id", "=", partner_id)], limit=1)

        for d in data:
            print(d)
            if "product_id" in d and "qty" in d:
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

        if sale_sudo.validate_presale():
            vals["presale"] = True

        sale_order = sale_sudo.create(vals)
        return sale_order.id

    @http.route(
        "/website_quick_quotation/load_products_data",
        type="json",
        auth="public",
        website=True,
    )
    def load_products_data(self, partner_id, **kw):

        partner_id = request.env.user.partner_id
        # partner_id = (
        #     request.env["res.partner"].sudo().search([("id", "=", partner_id)], limit=1)
        # )

        pricelist_id = partner_id.property_product_pricelist

        if not pricelist_id:
            pricelist_id = request.env.ref("product.list0", False)

        filter_mode = partner_id.filter_mode

        domain = []
        if filter_mode == "brand_only":

            brand_ids = partner_id.sudo().website_available_brand_ids

            if brand_ids:
                domain = [
                    (
                        "product_brand_id",
                        "in",
                        brand_ids.ids,
                    )
                ]

        product_model = request.env["product.product"].sudo()

        if domain:
            product_template_ids = request.env["product.template"].sudo().search(domain)
            if product_template_ids:
                domain = [("product_tmpl_id", "in", product_template_ids.ids)]

        product_ids = product_model.search(domain)

        data = []

        for record in product_ids:
            price = pricelist_id.get_product_price(record, 1, partner_id)

            data.append(
                {
                    "id": record.id,
                    "name": '%s - <span class="badge">%s</span>'
                    % (record.display_name, record.outgoing_qty),
                    "uom_id": (record.uom_id.sudo().id, record.uom_id.sudo().name),
                    "price": price,
                    "total": price,
                }
            )

        return data
