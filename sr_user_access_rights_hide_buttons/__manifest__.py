# -*- coding: utf-8 -*-
##############################################################################
#
#    OpenERP, Open Source Management Solution
#    Copyright (C) Sitaram Solutions (<https://sitaramsolutions.in/>).
#
#    For Module Support : info@sitaramsolutions.in  or Skype : contact.hiren1188
#
##############################################################################

{

    'name': "Hide and Show Feature for Create, Edit, Duplicate, Delete, Import, Export, Print, And Action",
    'version': '14.0.0.0',
    'category': 'Extra Addons',
    "license": "OPL-1",
    'summary': "This odoo application help you to hide and show create, edit, delete, import, export, print and action button user wise hide feature sitaram solutions application odoo erp hide button action menu hide action button hide",
    'description': """
            This odoo application help you to hide and show button
            hide and show action button
            hide and show action menu
            hide create button
            show create button
            hide edit button
            show edit button
            hide delete action button
            show delete action button
            hide import action button
            show import action button
            hide export action button
            show export action button
            hide print action button
            show print action button
            hide action menu
            show action menu
            specific user wise access right
            stop all the operation functionality for specific user
            hide and show feature in odoo
            sitaram solutions odoo application for hide and show application in odoo
            hide main form button
            hide main operational button
            show main form button
            show main operational button
            offer only see access right for user
            hide button
            show buttons
    """,
    "price": 10,
    "currency": 'EUR',
    'author': 'Sitaram',
    'depends': ['base', 'web'],
    'data': [
        "security/sr_user_access_groups.xml",
        "views/assets_backend_view.xml",
    ],
    'website':'https://sitaramsolutions.in',
    'installable': True,
    'auto_install': False,
    'live_test_url':'https://youtu.be/GeG_SleIsg0',
    "images":['static/description/banner.png'],
}
