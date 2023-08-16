# -*- coding: utf-8 -*-
{
    'name': "website_qty_cart",

    'summary': """
        cantidades en carrito de compras""",

    'description': """
        cantidades en carrito de compras
    """,

    'author': "GDCP",
    'category': 'website',
    'version': '0.1',

    # any module necessary for this one to work correctly
    'depends': ['base','website_sale','wt_product_seller'],

    # always loaded
    'data': [
        # 'security/ir.model.access.csv',
        'views/assets.xml',
        'views/templates.xml',
    ]
}
