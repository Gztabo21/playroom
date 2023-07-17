# -*- coding: utf-8 -*-
# Part of BrowseInfo. See LICENSE file for full copyright and licensing details.
{
    'name' : "Send Customer Birthday Wishes",
    'version' : "14.0.0.0",
    'author' : "Jimmy Araujo",
    'summary': 'Enviar saludos de cumpleaños por correo electrónico al socio/cliente',
    'description' : '''
            Módulo para enviar un Email a cliente en Cumpleaños.
enviar deseos de cumpleaños al cliente, correo electrónico de deseos de cumpleaños al cliente, correo electrónico de recordatorio de cumpleaños, correo electrónico de saludos de cumpleaños al cliente. enviar deseos de cumpleaños a un socio, correo electrónico de deseos de cumpleaños a un socio, correo electrónico de recordatorio de cumpleaños, correo electrónico de saludos de cumpleaños a un socio. 
    ''',
    'license':'OPL-1',
    'category' : "Extra Tools",
    'data': [
             'views/res_partner_view.xml',
             'views/birthday_reminder_cron.xml',
             'edi/birthday_reminder_action_data.xml'
             ],
    
    'depends' : ['sale'],
    'installable': True,
    'auto_install': False,
    "images":['static/description/Banner.png'],
}

# vim:expandtab:smartindent:tabstop=4:softtabstop=4:shiftwidth=4:
