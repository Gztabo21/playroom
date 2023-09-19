# -*- coding: utf-8 -*-
from datetime import datetime, timedelta
from odoo import api, fields, models, tools, SUPERUSER_ID
from odoo.http import request


class WebsiteInherit(models.Model):
    _inherit = "website"

    def sale_get_order(
        self,
        force_create=False,
        code=None,
        update_pricelist=False,
        force_pricelist=False,
    ):
        res = super(WebsiteInherit, self).sale_get_order(
            force_create, code, update_pricelist, force_pricelist
        )
        if res:
            res.update_presale()

        return res
