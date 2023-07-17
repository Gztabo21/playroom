# -*- coding: utf-8 -*-
##############################################################################
#
#    OpenERP, Open Source Management Solution
#    Copyright (C) 2004-2010 Tiny SPRL (<http://tiny.be>).
#
#    This program is free software: you can redistribute it and/or modify
#    it under the terms of the GNU Affero General Public License as
#    published by the Free Software Foundation, either version 3 of the
#    License, or (at your option) any later version.
#
#    This program is distributed in the hope that it will be useful,
#    but WITHOUT ANY WARRANTY; without even the implied warranty of
#    MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE.  See the
#    GNU Affero General Public License for more details.
#
#    Autor: Brayhan Andres Jaramillo Castaño
#    Correo: brayhanjaramillo@hotmail.com
#
#    You should have received a copy of the GNU Affero General Public License
#    along with this program.  If not, see <http://www.gnu.org/licenses/>.
#
##############################################################################

from odoo import api, fields, models, _


class AccountMoveInherit(models.Model):
    _inherit = "account.move"

    @api.depends("posted_before", "state", "journal_id", "date")
    def _compute_name(self):
        super(AccountMoveInherit, self)._compute_name()
        for record in self:
            journal_id = record.journal_id
            if journal_id:
                if record.state == "posted":
                    if record.payment_id:
                        partner_type = record.payment_id.partner_type
                        if partner_type == "customer":
                            sequence_id = journal_id.secure_sequence_id
                            if sequence_id:
                                record.name = sequence_id.next_by_id()
                        if partner_type == "supplier":
                            sequence_supplier_id = journal_id.sequence_supplier_id
                            if sequence_supplier_id:
                                record.name = sequence_supplier_id.next_by_id()
