# -*- coding: utf-8 -*-
from odoo import api, fields, models, _
from odoo.exceptions import UserError

class MergeWizard(models.TransientModel):
    _name = 'sale.merge.wizard'
    _description = 'Merge Record'

    partner_id = fields.Many2one('res.partner', 'Customer/Supplier', required=True)
    sale_id = fields.Many2one('sale.order', 'Sale Order')
    create_new_record = fields.Boolean('Create New Record', default=True)
    merge_in_record = fields.Boolean('Merge in Existing Record')
    order_todo =  fields.Selection([
            ('cancel','Cancel Orders'),
            ('delete','Delete Orders'),
        ], 'Cancel/Delete Other Orders', default='cancel' ,required=True)

    @api.model
    def default_get(self, fields):
        active_model = self._context.get('active_model')
        res = super(MergeWizard, self).default_get(fields)

        if len(self._context.get('active_ids'))<=1:
            raise UserError(_('Select two or more than two records.'))

        partner_group = self.env[active_model].read_group([('id', 'in', self._context.get('active_ids', []))] , fields=['partner_id'], groupby=['partner_id'])
        if len(partner_group) > 1:
            raise UserError(_('Select records for same Customer/Supplier.'))

        non_draft_orders = self.env[active_model].browse(self._context.get('active_ids')).filtered(lambda s: s.state!='draft')
        if len(non_draft_orders) >= 1:
            raise UserError(_('Select records which are in draft state.'))

        active_record = self.env[active_model].browse(self._context.get('active_ids')[0])
        res.update({'partner_id': active_record.partner_id.id})
        if active_model == 'sale.order':
            warehouse_group = self.env[active_model].read_group([('id', 'in', self._context.get('active_ids', []))] , fields=['warehouse_id'], groupby=['warehouse_id'])
            if len(warehouse_group) > 1:
                raise UserError(_('Select records for same Warehouse.'))
        return res

    @api.onchange('create_new_record')
    def onchange_create_new_record(self):
        if self.create_new_record:
            self.merge_in_record = False
        else:
            self.merge_in_record = True

    @api.onchange('merge_in_record')
    def onchange_merge_in_record(self):
        if self.merge_in_record:
            self.create_new_record = False
        else:
            self.create_new_record = True

    def merge_record(self):
        active_model = self._context.get('active_model')
        active_records = self.env[active_model].browse(self._context.get('active_ids'))
        origin = ''
        for record in active_records:
            if record.origin:
                origin += record.origin + ', '
        origin = origin[:-2]
        if active_model == 'sale.order':
            SaleLine = self.env['sale.order.line']
            records_to_copy = active_records
            if self.create_new_record:
                rec_to_exclude = active_records[0]
                records_to_copy = active_records - rec_to_exclude
                new_rec_id = rec_to_exclude.copy()
                
                if self.order_todo=='cancel':
                    rec_to_exclude.action_cancel()
                    rec_to_exclude.message_post(body=_("Record Merged in: %s") % new_rec_id.name)
                else:
                    rec_to_exclude.unlink()

            else:
                records_to_copy = active_records - self.sale_id
                new_rec_id = self.sale_id

            new_rec_id.origin = origin
            for rec in records_to_copy:
                for line in rec.order_line:
                    same_line = SaleLine.search([('order_id', '=', new_rec_id.id),
                        ('product_id','=',line.product_id.id),
                        ('price_unit','=',line.price_unit),
                        ('discount','=',line.discount),
                        ('name','=',line.name),
                    ], limit=1)
                    if same_line:
                        same_line.product_uom_qty += line.product_uom_qty
                    else:
                        line.copy({'order_id': new_rec_id.id})

            if self.order_todo=='cancel':
                records_to_copy.action_cancel()
                records_to_copy.message_post(body=_("Record Merged in: %s") % new_rec_id.name)
            else:
                records_to_copy.unlink()

            action = self.env["ir.actions.actions"]._for_xml_id("sale.action_quotations")
            action['views'] = [(self.env.ref('sale.view_order_form').id, 'form')]
            action['res_id'] = new_rec_id.id
            return action