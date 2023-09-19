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

from odoo import api, fields, models, _
from datetime import datetime


class ResPartnerInherit(models.Model):
    _inherit = "res.partner"

    @api.depends("category_id")
    def compute_is_collector(self):
        for record in self:
            is_collector = False
            if record.category_id:
                for item in record.category_id:
                    if item.name == "Mensajeros":
                        is_collector = True
            record.is_collector = is_collector

    is_collector = fields.Boolean(
        string="¿Es Cobrador?", compute=compute_is_collector, store=True
    )
