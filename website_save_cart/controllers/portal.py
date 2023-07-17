# -*- coding: utf-8 -*-

from odoo import http
from odoo.addons.portal.controllers.portal import CustomerPortal, pager as portal_pager
from odoo.http import request


class PortalAccount(CustomerPortal):

    def _get_save_cart_domain(self):
        partner = request.env.user.partner_id
        domain = [('partner_id', '=', partner.id)]
        return domain

    def _prepare_portal_layout_values(self):
        values = super(PortalAccount, self)._prepare_portal_layout_values()
        carts_count = request.env['save.cart'].search_count(self._get_save_cart_domain())
        values['carts_count'] = carts_count
        return values

    def _save_cart_get_page_view_values(self, cart, **kwargs):
        values = {
            'page_name': 'carts',
            'cart': cart,
            'save_carts': request.env['save.cart'].sudo().search([])
        }
        if kwargs.get('error'):
            values['error'] = kwargs['error']
        if kwargs.get('warning'):
            values['warning'] = kwargs['warning']
        if kwargs.get('success'):
            values['success'] = kwargs['success']
        return values

    @http.route(['/my/carts', '/my/carts/page/<int:page>'], type='http', auth="user", website=True)
    def portal_my_carts(self, page=1, date_begin=None, date_end=None, **kw):
        values = self._prepare_portal_layout_values()
        # partner = request.env.user.partner_id
        SaveCart = request.env['save.cart']

        domain = self._get_save_cart_domain()

        if date_begin and date_end:
            domain += [('create_date', '>', date_begin), ('create_date', '<=', date_end)]

        # count for pager
        carts_count = SaveCart.sudo().search_count(domain)
        # pager
        pager = portal_pager(
            url="/my/carts",
            url_args={'date_begin': date_begin, 'date_end': date_end},
            total=carts_count,
            page=page,
            step=self._items_per_page
        )
        # content according to pager and archive selected
        save_carts = SaveCart.sudo().search(domain, limit=self._items_per_page, offset=pager['offset'])
        values.update({
            'date': date_begin,
            'save_carts': save_carts,
            'page_name': 'carts',
            'pager': pager,
            'default_url': '/my/carts'
        })
        return request.render("website_save_cart.portal_my_save_cart", values)

    @http.route(['/my/carts/<int:cart_id>'], type='http', auth="public", website=True)
    def portal_my_invoice_detail(self, cart_id, **kw):
        save_cart_sudo = request.env['save.cart'].browse([cart_id])
        cart_sudo = save_cart_sudo.sudo()
        values = self._save_cart_get_page_view_values(cart_sudo, **kw)
        return request.render("website_save_cart.portal_save_cart_page", values)
