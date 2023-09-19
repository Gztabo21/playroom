# -*- coding: utf-8 -*-
# Part of Softhealer Technologies.

{
    "name": "Purchase Discount",
    "author": "Softhealer Technologies",
    "website": "https://www.softhealer.com",
    "support": "support@softhealer.com",
    "license": "OPL-1",
    "category": "Purchases",
    "summary": "Purchase Order Discount,Purchases Discount,Purchase Line Discount,Purchase Order Line Discount,Discount On Purchase Line,Discount On Purchase Order Lines, fixed discount,fix discount,Purchase Product Discount Odoo",
    "description": """This module allows to add the discount per line in the purchase orders. You can apply a different discount on each order. You can even specify multiple discounts on the same product on each order. In the purchase order report discount is also included.""",
    "version": "14.0.2",
    "depends": ["purchase"],
    "data": [
        'security/discount_security.xml',
        'report/po_report.xml',
        'views/purchase_order.xml',
        

    ],
    "auto_install": False,
    "installable": True,
    "application": True,
    "images": ["static/description/background.png", ],
    "price": "15",
    "currency": "EUR"
}
