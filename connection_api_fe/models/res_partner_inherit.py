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


class ResPartnerInherit(models.Model):
    _inherit = "res.partner"

    PERSON_TYPE = [("1", "Natural"), ("2", "Juridical")]

    @api.model
    def _default_fiscal_responsability(self):
        data = []
        fiscal_responsability_ids = self.env["dian.fiscal.responsability"].search(
            [("code", "=", "O-49")]
        )
        if fiscal_responsability_ids:
            data.append((6, 0, [x.id for x in fiscal_responsability_ids]))
        return data

    fiscal_responsability_ids = fields.Many2many(
        "dian.fiscal.responsability",
        string="Responsabilidad fiscal",
        default=_default_fiscal_responsability,
    )
    personType = fields.Selection(PERSON_TYPE, "Type of Person", default="1")
