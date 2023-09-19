# -*- coding: utf-8 -*-
{
    'name': "website_short_cart",

    'summary': """
        Corta los pasos de funcionar y procesar el pago en la website""",

    'description': """
        Corta los pasos de funcionar y procesar el pago en la website
    """,

    'author': "dooit",
    'category': 'website',
    'version': '14.0.1',

    # any module necessary for this one to work correctly
    'depends': ['base','website','website_save_cart'],

    # always loaded
    'data': [
        'views/assest.xml',
        'views/templates.xml',
    ],
}
