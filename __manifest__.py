# -*- coding: utf-8 -*-
{
    'name': "Sala de play",

    'summary': """
        Sala para administrar consolas de videojuegos
        """,

    'description': """
        Sala para administrar consolas de videojuegos
    """,

    'author': "Gustavo Cacharuco",
    'website': "mailto:gustavocacharuco@gmail.com?subject=Support%20playroom",

    'category': 'Uncategorized',
    'version': '0.1',
    'depends': ['base'],
    'licenses':'LGPL-3',
    'data': [
        'security/ir.model.access.csv',
        'data/console_type.xml',
        'data/game.xml',
        'data/sequence_ticket.xml',
        'report/report_ticket.xml',
        'views/views.xml',
        'views/res_partner_view.xml',
        'views/menu.xml'
    ],
    
}
