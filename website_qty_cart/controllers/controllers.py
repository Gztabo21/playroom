# -*- coding: utf-8 -*-
# from odoo import http


# class WebsiteQtyCart(http.Controller):
#     @http.route('/website_qty_cart/website_qty_cart/', auth='public')
#     def index(self, **kw):
#         return "Hello, world"

#     @http.route('/website_qty_cart/website_qty_cart/objects/', auth='public')
#     def list(self, **kw):
#         return http.request.render('website_qty_cart.listing', {
#             'root': '/website_qty_cart/website_qty_cart',
#             'objects': http.request.env['website_qty_cart.website_qty_cart'].search([]),
#         })

#     @http.route('/website_qty_cart/website_qty_cart/objects/<model("website_qty_cart.website_qty_cart"):obj>/', auth='public')
#     def object(self, obj, **kw):
#         return http.request.render('website_qty_cart.object', {
#             'object': obj
#         })
