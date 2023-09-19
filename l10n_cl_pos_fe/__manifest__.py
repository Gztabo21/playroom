# -*- coding: utf-8 -*-
{
    'name': "POS - Boleta Electrónica",

    'summary': """
        Emisión de Boletas desde el POS""",

    'description': """
        Emisión de Boletas desde el POS
    """,

    'author': "CMCorp",
    'website': "https://cmcorp.odoo.com",
    'category': 'Uncategorized',
    'version': '0.1',

    # any module necessary for this one to work correctly
    'depends': ['point_of_sale',
                'l10n_cl',
                'l10n_cl_edi_boletas',
                'l10n_latam_invoice_document',
                ],

    # always loaded
    'data': [
        #'views/assets.xml',
        'views/pos_config_views.xml',
        'views/pos_order_views.xml',
    ],
    'assets': {
        'point_of_sale.assets': [
            'l10n_cl_pos_fe/static/src/less/pos.less',
            'l10n_cl_pos_fe/static/src/js/models.js',
            'l10n_cl_pos_fe/static/src/js/Screens/PaymentScreen/PaymentScreen.js',
            'l10n_cl_pos_fe/static/src/js/Screens/PaymentScreen/OrderReceipt.js',
            'l10n_cl_pos_fe/static/src/lib/pdf417-min.js'
        ],
        'web.assets_qweb': [
            'l10n_cl_pos_fe/static/src/xml/**/*',
        ],
    },
    'installable': True,
    'auto_install': False,
    'demo': [],
    'test': [],
}