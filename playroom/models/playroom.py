# -*- coding: utf-8 -*-

from odoo import models, fields, api
from odoo.addons.resource.models.resource import float_to_time

class playroom(models.Model):
    _name = 'gd.playroom'
    _description = 'Playroom'

    name = fields.Char('Nombre', default="Nuevo")
    use_time = fields.Float('Tiempo',digits=(2,2))
    gamer_id = fields.Many2one('res.partner','Jugador', domain=[('is_gamer','=', True)])
    game_ids =  fields.Many2many('gd.game',string='Juegos')
    console_type_id =  fields.Many2one('console.type','Consola')
    description = fields.Text('Descripción')


    def action_confirm(self):
        if self.name == 'Nuevo':
            self.name = self.env['ir.sequence'].next_by_code('seq.ticket.playroom')
            return self.env.ref('playroom.action_report_receipt_ticket').report_action(self)   


    def float_to_time(self,hours):
        return float_to_time(hours)
         