# -*- coding: utf-8 -*-

from odoo import models, fields, api

class PosConfig(models.Model):
    _inherit = 'pos.config'

    module_ticket = fields.Boolean(string='Usar Boletas', default=True)
    required_document = fields.Boolean(string='Documentos Obligatorios', default=False)
