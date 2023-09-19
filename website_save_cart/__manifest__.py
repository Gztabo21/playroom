# -*- coding: utf-8 -*-
{
    'name': "Website Sale Save Cart",
    'version': '1.0',
    'summary': 'Website Sale Save Cart Manager Multiple cart and feature use',
    'description': """
Website Sale Save Cart Manager Multiple cart and feature use.
=============================================================
    """,
    'author': "Do Incredible",
    'website': "http://doincredible.com",
    'category': 'eCommerce',
    'depends': ['website_sale'],
    'data': [
        'security/ir.model.access.csv',
        'views/website_backend_views.xml',
        'views/assest.xml',
        'views/website_template.xml',
    ],
    'images': ['static/description/main_image.png'],
    'price': 35,
    'currency': 'USD',
    'license': 'OPL-1',
    'installable': True,
    'application': True,
    'live_test_url': 'https://youtu.be/OBiPVFmY62A',
}
