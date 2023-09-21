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
    "name": "Multi Product PO",
    "version": "14.0",
    "category": "sale",
    "author": "Brayhan Andres Jaramillo Castaño",
    "summary": "Modulo que permite agregar varios productos a la orden de compra",
    "website": "",
    "depends": [
        "purchase",
        "product",
    ],
    "data": [
        "security/ir.model.access.csv",
        "views/purchase_order_inherit_view.xml",
        "wizard/multi_product_select_view.xml",
    ],
    "demo": [],
    "installable": True,
    "auto_install": False,
}