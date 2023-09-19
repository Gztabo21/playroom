# -*- coding: utf-8 -*-
from datetime import datetime, timedelta
from odoo import api, fields, models, tools, SUPERUSER_ID
from odoo.http import request

class Website(models.Model):
    _inherit = 'website'

    def sale_get_order(self, force_create=False, code=None, update_pricelist=False, force_pricelist=False):
        res = super(Website, self).sale_get_order(force_create, code, update_pricelist, force_pricelist)
        if res and res.state == 'draft' and res.seller_partner_id and res.seller_partner_id != res.partner_id:
            pricelist = res.pricelist_id.sudo()
            partner = res.seller_partner_id if res.seller_partner_id else res.partner_id
            so_data = self._prepare_sale_order_values(partner, pricelist)
            res.with_company(request.website.company_id.id).with_user(SUPERUSER_ID).write(so_data)
        if res and res.seller_partner_id:
            res.write({'partner_id': res.seller_partner_id.id})
        return res