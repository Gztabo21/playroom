# -*- coding: utf-8 -*

from odoo import fields,models,api


class InheritResPartner(models.Model):
    _inherit = 'res.partner'

    is_gamer = fields.Boolean('Jugador', default=False)
    # first_name
    second_name = fields.Char('Segundo Nombre')
    first_lastname = fields.Char('Primer Apellido')
    second_lastname = fields.Char('Segundd Apellido')

    def name_get(self):
        result = []
        for rec in self:
            result.append((rec.id, '%s %s' % (rec.name, rec.first_lastname)))
        return result