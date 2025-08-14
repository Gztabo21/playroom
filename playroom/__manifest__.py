# -*- coding: utf-8 -*-
{
    "name": "Playroom",
    "summary": """
        Sala para administrar consolas de videojuegos
        """,
    "description": """
        Sala para administrar consolas de videojuegos
    """,
    "author": "Gustavo Cacharuco",
    "website": "mailto:gustavocacharuco@gmail.com?subject=Support%20playroom",
    "category": "base",
    "version": "1.0.0",
    "depends": ["base"],
    "application": True,
    "license": "LGPL-3",
    "images":['static/description/banner.png'],
	"data": [
        "security/ir.model.access.csv",
        "data/console_type.xml",
        "data/game.xml",
        "data/sequence_ticket.xml",
        "report/report_ticket.xml",
        "views/views.xml",
        "views/res_partner_view.xml",
        "views/menu.xml",
    ],
}
