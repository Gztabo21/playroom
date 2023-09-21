# -*- coding: utf-8 -*-
# Copyright 2023 Jimmy Araujo
# License AGPL-3.0 or later (http://www.gnu.org/licenses/agpl).

{
    "name": "Kal Account Report",
    "version": "14.0.0.1",
    "author": "DOOIT",
    "license": "AGPL-3",
    "depends": ['account_reports'],
    "data": [
        'views/assets.xml',
        'views/account_view_report_aged_recivable.xml',
    ],
    'qweb': [
        'static/src/xml/account_report_template.xml',
    ],
    "installable": True,
}