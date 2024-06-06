# -*- coding: utf-8 -*-

from odoo import fields, api ,models, _
from datetime import datetime

class ConsoleType(models.Model):
    _name = "console.type"
    _description = "Tipo de consola de video juego"

    name = fields.Char('Nombre')
    code = fields.Char('codigo')
    console_color = fields.Char('Color')
    description = fields.Text('Description')
    release_date = fields.Datetime('Fecha de lanzamiento', default=datetime.today())
