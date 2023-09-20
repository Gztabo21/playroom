# -*- coding: utf-8 -*-
###############################################################################
#                                                                             #
#                                                                             #
# Part of Odoo. See LICENSE file for full copyright and licensing details.    #
#                                                                             #
#                                                                             #
# Copyright (C)                                               				  #
#    Autor: Brayhan Andres Jaramillo Castaño								  #
#    Correo: brayhanjaramillo@hotmail.com 		                  			  #
#                                                                             #
# Co-Authors    Odoo LoCo                                                     #
#               Localización funcional de Odoo para Colombia                  #
#                                                                             #
###############################################################################


from odoo import models, fields, api, exceptions
from odoo.tools.translate import _
from odoo import SUPERUSER_ID, api, fields, models, _
import re
import logging

_logger = logging.getLogger(__name__)


class ResCIIU(models.Model):
    _name = "res.ciiu"
    _description = "CIIU Codes"
    _parent_name = "parent_id"

    _parent_order = "code, name"
    _order = "parent_left"

    name = fields.Char(string="Name", help="CIIU Nmae", required=True)
    display_name = fields.Char(string="Display Name", compute="_compute_display_name")
    code = fields.Char(string="Code", help="CIIU code.", required=True)
    note = fields.Text(string="Note")
    type = fields.Selection(
        string="Type",
        selection=[("view", "view"), ("other", "other")],
        help="Registry type",
        required=True,
    )
    parent_id = fields.Many2one("res.ciiu", string="Parent", ondelete="set null")
    child_ids = fields.One2many(
        string="Childs Codes", comodel_name="res.ciiu", inverse_name="parent_id"
    )
    parent_left = fields.Integer("Parent Left")
    parent_right = fields.Integer("Parent Right")

    _sql_constraints = [
        ("name_uniq", "unique (code)", "The code of CIIU must be unique !")
    ]

    @api.depends("code", "name")
    def _compute_display_name(self):
        for ciiu in self:
            ciiu.display_name = "[%s] %s" % (ciiu.code, ciiu.name)

    @api.model
    def name_search(self, name, args=None, operator="ilike", limit=100):
        if not args:
            args = []
        if name:
            ciiu = self.search(
                ["|", ("name", operator, name), ("code", operator, name)] + args,
                limit=limit,
            )
        else:
            ciiu = self.search(args, limit=limit)

        return ciiu.name_get()

    def name_get(self):
        res = []
        for record in self:
            name = record.name
            if record.code:
                name = u"[%s] %s" % (record.code, name)
            res.append((record.id, name))
        return res

    def action_parent_store_compute(self):
        self._parent_store_compute()


ResCIIU()
