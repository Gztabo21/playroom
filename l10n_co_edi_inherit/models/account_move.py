# -*- coding: utf-8 -*-

from odoo import models,api,fields,_ 


class InheritAccountMove(models.Model):
    _inherit = "account.move"
    _description = "Agrega una nueva nota"


    def _l10n_co_edi_get_notas(self):
        res = super(InheritAccountMove,self)._l10n_co_edi_get_notas()
        if self.move_type not in ['in_invoice','in_refund']:
            shipping_partner = self.env['res.partner'].browse(self._get_invoice_delivery_partner_id())
            res.append(
                '12.- |%s ' % (shipping_partner.street)
            )
        #res.append({'':''})
        return res
