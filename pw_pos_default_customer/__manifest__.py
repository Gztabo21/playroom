# -*- coding: utf-8 -*-
{
    'name': 'POS Default Customer',
    'version': '14.0',
    'author': 'Preway IT Solutions',
    'category': 'Point of Sale',
    'depends': ['point_of_sale'],
    'summary': 'This apps helps you set default customer on POS',
    'description': """
- Default customer on POS.
    """,
    'data': [
        'views/point_of_sale.xml',
        'views/pos_config_view.xml',
    ],
    'application': True,
    'installable': True,
    "images":["static/description/Banner.png"],
}
