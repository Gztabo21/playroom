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


class AccountTaxInherit(models.Model):
    _inherit = "account.tax"

    TYPE_TAX_DIAN = [
        ("01", "IVA"),
        ("02", "IC"),
        ("03", "ICA"),
        ("04", "INC"),
        ("20", "FtoHorticultura"),
        ("21", "Timbre"),
        ("22", "INC Bolsas"),
        ("23", "INCarbono"),
        ("24", "INCombustibles"),
        ("25", "Sobretasa Combustibles"),
        ("26", "Sordicom"),
        ("ZA", "IVA e INC"),
        ("ZY", "No Causa"),
        ("ZZ", "No Aplica"),
        ("05", "ReteIVA"),
        ("06", "ReteFuente"),
        ("07", "ReteICA"),
    ]

    type_tax_dian = fields.Selection(
        TYPE_TAX_DIAN, string="Tipo Impuesto", default="ZZ"
    )
    validate_dian = fields.Boolean(string="Validar DIAN", default=False)
    show_in_report = fields.Boolean(string="¿Mostrar en reporte?", default=True)
