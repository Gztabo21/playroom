# -*- coding: utf-8 -*-

from odoo import http
from odoo.http import request


class SaveCart(http.Controller):

    @http.route(['/shop/multicart/add'], type='http', auth="user", methods=['POST', 'GET'], website=True)
    def add_multicart(self, **kw):
        order = request.website.sale_get_order()
        if kw.get('cart_name') and order:
            if order.state in ['draft', 'sent']:
                save_cart_lines = []
                if order.order_line:
                    for line in order.order_line:
                        save_cart_lines.append((0, 0, {'product_id': line.product_id.id,
                                                       'product_uom_qty': line.product_uom_qty,
                                                       'product_uom': line.product_uom.id,
                                                       'price_unit': line.price_unit}))
                request.env['save.cart'].sudo().create({'name': kw.get('cart_name'),
                                                        'sale_order_id': order.id,
                                                        'partner_id': request.env.user.partner_id.id,
                                                        'cart_lines': save_cart_lines})

        return request.redirect(request.httprequest.referrer)

    @http.route(['/shop/multicart/rename'], type='http', auth="user", methods=['POST', 'GET'], website=True)
    def rename_multicart(self, **kw):
        if kw.get('cart_name') and kw.get('cart_id'):
            save_cart_id = request.env['save.cart'].sudo().browse(int(kw.get('cart_id')))
            save_cart_id.write({'name': kw.get('cart_name')})

        return request.redirect(request.httprequest.referrer)

    @http.route(['/shop/multicart/move'], type='http', auth="user", methods=['POST', 'GET'], website=True)
    def move_multicart(self, **kw):
        order = request.website.sale_get_order()
        if kw.get('cart_id'):
            save_cart_id = request.env['save.cart'].sudo().browse(int(kw.get('cart_id')))
            if kw.get('marge_cart') and order:
                for line in save_cart_id.cart_lines:
                    request.website.sale_get_order(force_create=1)._cart_update(product_id=line.product_id.id, add_qty=line.product_uom_qty)
            elif kw.get('replace_cart') and order:
                order.order_line = False
                order.order_line
                save_cart_lines = []
                for line in save_cart_id.cart_lines:
                    save_cart_lines.append((0, 0, {'product_id': line.product_id.id,
                                                   'product_uom_qty': line.product_uom_qty,
                                                   'product_uom': line.product_uom.id,
                                                   'price_unit': line.price_unit}))
                order.order_line = save_cart_lines
            elif kw.get('current_marge_cart') and kw.get('slected_cart'):
                selected_cart_id = request.env['save.cart'].sudo().browse(int(kw.get('slected_cart')))
                for line in save_cart_id.cart_lines:
                    selected_orderline_find = request.env['save.cart.line'].sudo().search([('save_cart_id', '=', selected_cart_id.id), ('product_id', '=', line.product_id.id)])
                    last_orderline_find = request.env['save.cart.line'].sudo().search([('save_cart_id', '=', save_cart_id.id), ('product_id', '=', line.product_id.id)])
                    if selected_orderline_find and last_orderline_find:
                        selected_orderline_find.product_uom_qty += last_orderline_find.product_uom_qty
                    else:
                        last_orderline_find.save_cart_id = selected_cart_id.id
                save_cart_id.sudo().unlink()
                return request.redirect('/my/carts')

        return request.redirect('/shop/cart')
