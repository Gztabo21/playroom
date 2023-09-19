# -*- coding: utf-8 -*-
##############################################################################
#
#    OpenERP, Open Source Management Solution
#    Copyright (C) 2004-2010 Tiny SPRL (<http://tiny.be>).
#
#    This program is free software: you can redistribute it and/or modify
#    it under the terms of the GNU Affero General Public License as
#    published by the Free Software Foundation, either version 3 of the
#    License, or (at your option) any later version.
#
#    This program is distributed in the hope that it will be useful,
#    but WITHOUT ANY WARRANTY; without even the implied warranty of
#    MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE.  See the
#    GNU Affero General Public License for more details.
#
#    Autor: Brayhan Andres Jaramillo Castaño
#    Correo: brayhanjaramillo@hotmail.com
#
#    You should have received a copy of the GNU Affero General Public License
#    along with this program.  If not, see <http://www.gnu.org/licenses/>.
#
##############################################################################

from odoo import fields, models


class SaleReportInherit(models.Model):
    _inherit = "sale.report"

    brand_id = fields.Many2one("product.brand", "Brand", readonly=True)

    def _query(self, with_clause="", fields={}, groupby="", from_clause=""):
        fields["brand_id"] = ", t.brand_id as brand_id"
        groupby += ", t.brand_id"
        return super(SaleReportInherit, self)._query(
            with_clause, fields, groupby, from_clause
        )
