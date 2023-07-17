# -*- coding: utf-8 -*-
# Part of Odoo. See COPYRIGHT & LICENSE files for full copyright and licensing details.

{
    "name": "Customer Selection website / Website Agent Login",
    "version": "14.0.1",
    "category": "website",
    "summary": "Customer Selection website / Website Agent Login ",
    "description": """
        Create Salesorder for any customer using agent login.
    """,
    "author": "Warlock Technologies Pvt Ltd.",
    "website": "http://warlocktechnologies.com",
    "support": "support@warlocktechnologies.com",
    "depends": ['base', 'sale', 'website', 'website_sale', 'website_sale_wishlist'],
    "data": [
        'security/ir.model.access.csv',
        "views/sale_order_view.xml",
        "views/template.xml",
        "views/assets.xml",
        "views/res_users_view.xml",
        "views/order_history_template.xml",
    ],
    "images": ["images/screen.png"],
    "license": "OPL-1",
    "price": 50,
    "currency": "USD",
    "application": True,
    "installable": True,
}
