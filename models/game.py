# -*- coding: utf-8 -*-

from odoo import fields,api,models

class Game(models.Model):
    _name = "gd.game"
    _description = "Juegos"

    name = fields.Char('Nombre')
    code = fields.Char('Codigo')
    is_multi_gamer = fields.Boolean('Multijugador',default=False)
    image_game = fields.Binary('Imagen')
    age_range = fields.Char('Rango de edad')