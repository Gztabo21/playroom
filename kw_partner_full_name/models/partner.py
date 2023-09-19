import logging

from odoo import fields, models, api

_logger = logging.getLogger(__name__)


class ResPartner(models.Model):
    _inherit = 'res.partner'
    _sql_constraints = [
        ('check_name', "Check(1=1)", 'Contacts require a name'), ]

    kw_partner_first_name = fields.Char(
        string='First name', )
    kw_partner_middle_name = fields.Char(
        string='Middle name', )
    kw_partner_last_name = fields.Char(
        string='Last name', )
    kw_is_partner_fullname = fields.Boolean(
        compute='_compute_kw_is_partner_fullname', )
    kw_computed_name = fields.Char(
        string='Full name', compute='_compute_kw_computed_name')

    @api.depends('type', 'is_company')
    def _compute_kw_is_partner_fullname(self):
        for obj in self:
            obj.kw_is_partner_fullname = \
                obj.type in 'contact' and not obj.is_company

    def _compute_kw_computed_name(self):
        for obj in self:
            obj.kw_computed_name = obj.name

    @api.model
    def create(self, vals):
        if vals.get('name') and not vals.get('kw_partner_first_name'):
            vals['kw_partner_first_name'] = vals.get('name')
        if vals.get('type') == 'contact' and not vals.get('is_company'):
            vals['kw_is_partner_fullname'] = True
        else:
            vals['kw_is_partner_fullname'] = False
        return super(ResPartner, self).create(vals)

    def write(self, vals):
        p = ['name', 'kw_partner_first_name', 'kw_partner_middle_name',
             'kw_partner_last_name']
        if any([x in vals for x in p]):
            for obj in self:
                val = vals.copy()
                obj_is_company = vals.get('is_company') or obj.is_company
                obj_type = vals.get('type') or obj.type
                if obj_type in 'contact' and not obj_is_company:
                    val['name'] = '{} {} {}'.format(
                        val.get('kw_partner_first_name') or
                        obj.kw_partner_first_name or '',
                        val.get('kw_partner_middle_name') or
                        obj.kw_partner_middle_name or '',
                        val.get('kw_partner_last_name') or
                        obj.kw_partner_last_name or '', ).strip()
                else:
                    val['kw_partner_first_name'] = val.get('name')
                super(ResPartner, obj).write(val)
            return True
        return super(ResPartner, self).write(vals)
