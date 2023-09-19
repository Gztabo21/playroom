from odoo.addons.website_sale.controllers.main import WebsiteSale
from odoo.addons.website_sale_wishlist.controllers.main import WebsiteSaleWishlist
from odoo import fields, http, SUPERUSER_ID, tools, _
from odoo.http import request


class WebsiteSaleInherit(WebsiteSale):
    @http.route("/get_customer", type="json", auth="public", website=True)
    def get_customer(self, customer):
        request.session["website_sale_current_pl"] = None
        sale_order_id = request.website.sale_get_order(force_create=True)
        sale_order_id.sudo().update(
            {
                "seller_partner_id": customer,
                "is_seller": True,
            }
        )
        return True

    # @http.route(['/shop/confirmation'], type='http', auth="public", website=True, sitemap=False)
    # def payment_confirmation(self, **post):
    #     res = super(WebsiteSale, self).payment_confirmation(**post)
    #     sale_order_id = request.session.get('sale_last_order_id')
    #     if sale_order_id:
    #         order = request.env['sale.order'].sudo().browse(sale_order_id)
    #         if order.is_seller == True:
    #             order.sudo().update({
    #                 'user_id': request.env.user.id,
    #                 'partner_id': order.seller_partner_id.id,
    #                 })
    #             order.sudo().onchange_partner_id()
    #     return res

    @http.route("/customer/order/history", type="json", auth="public", website=True)
    def customer_order_history(self, customer=False, product=False):
        value = {}
        if product:
            product = request.env["product.product"].browse(product)

            order_lines = (
                request.env["sale.order.line"]
                .sudo()
                .search([])
                .filtered(
                    lambda s: s.order_id.partner_id.id == int(customer)
                    and s.order_id.state not in ["draft", "cancel"]
                    and s.product_id.id == int(product.id)
                )
            )
            value["product_order_history"] = request.env["ir.ui.view"]._render_template(
                "wt_product_seller.product_order_history",
                {
                    "order_lines": order_lines,
                    "sel_product": product,
                },
            )
            return value

    @http.route()
    def shop(self, page=0, category=None, search="", ppg=False, **post):
        partner_id = (
            request.env.user.partner_id.id
            if not request.website.is_public_user()
            else False
        )
        flag = True
        recent_products = []
        if request.env.user.is_seller:
            order = request.website.sale_get_order()
            if order and order.seller_partner_id:
                if order.seller_partner_id.property_product_pricelist:
                    request.session[
                        "website_sale_current_pl"
                    ] = order.seller_partner_id.property_product_pricelist.id
                    pr_id = request.session.get("website_sale_current_pl")
                    request.website.sale_get_order(force_pricelist=pr_id or False)
                partner_id = order.seller_partner_id.id
            else:
                flag = False

        res = super(WebsiteSaleInherit, self).shop(page, category, search, ppg, **post)
        return res
