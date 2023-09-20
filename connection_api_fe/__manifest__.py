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

{
    "name": "Conecction Api FE Syscord",
    "version": "14.0.0.0.0",
    "category": "account",
    "author": "Brayhan Andres Jaramillo Castaño",
    "summary": "Modulo que permite conectarse a la api de pagopass para la FE",
    "website": "",
    "depends": [
        "base",
        "account",
        "product",
        "base_address_city",
        "l10n_co",
        "l10n_latam_base",
        "sequence_models",
    ],
    "data": [
        "security/security.xml",
        "security/ir.model.access.csv",
        "data/res.city.csv",
        "data/sequence.xml",
        "data/l10n_latam_identification_type.xml",
        "data/dian_fiscal_responsability_data.xml",
        "data/product_unit_measure_fe_data.xml",
        "data/payment_methods_dian_data.xml",
        "data/mail_template_inherit.xml",
        "data/ir_cron_view.xml",
        "views/l10n_latam_identification_type_inherit_view.xml",
        "views/res_company_inherit_view.xml",
        "views/account_move_inherit_view.xml",
        "views/res_partner_inherit.xml",
        "views/product_product_inherit_view.xml",
        "views/account_tax_inherit_view.xml",
        "views/ir_sequence_view.xml",
        "views/account_journal_inherit.xml",
        # "views/base_document_layout_inherit_view.xml",
        "views/account_journal_inherit_view.xml",
        "views/ir_cron_view.xml",
        "report/report_invoice_fe.xml",
        "report/report_invoice_document_inherit.xml",
    ],
    "demo": [],
    "installable": True,
    "auto_install": False,
}
