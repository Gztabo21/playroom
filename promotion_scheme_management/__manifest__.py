# -*- coding: utf-8 -*-
# © 2018-Today Aktiv Software (http://www.aktivsoftware.com).
# Part of AktivSoftware See LICENSE file for full copyright
# and licensing details.
{
    'name': 'Promotion And Scheme Management',
    'category': 'Sales',
    'summary': 'Promotion And Scheme Management',
    'author': 'Aktiv Software',
    'website': 'https://www.aktivsoftware.com/',
    'version': '14.0.1.0.0',
    'license': 'AGPL-3',
    'description': "Promotion and Scheme Management on Sales order to manage sales channel.",
    'depends': ['sale_management'],
    'data': [
        'security/ir.model.access.csv',
        'views/promotion_scheme_view.xml',
        'views/sale_order_inherit_view.xml',
        'views/sale_reward_product_view.xml',
    ],
    'price': 15.00,
    'currency': "USD",
    'images': [
        'static/description/banner.jpg'
    ],
    'installable': True,
    'application': False,

}
