# -*- coding: utf-8 -*-
from odoo import http
from odoo.addons.website_save_cart.controllers.main import SaveCart
from odoo.http import request


class WebsiteShortCart(SaveCart):

    @http.route(['/shop/multicart/move'], type='http', auth="user", methods=['POST', 'GET'], website=True)
    def  move_multicart(self, **kw):
        res = super(WebsiteShortCart,self).move_multicart(**kw)
        if kw.get('cart_id') and kw.get('checkout_cart') :
            return request.redirect('/shop/checkout?express=1')
        return res 