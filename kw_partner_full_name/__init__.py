import logging

from odoo import api, SUPERUSER_ID

from . import models

_logger = logging.getLogger(__name__)


def kw_put_names_to_firstname(cr, registry):
    env = api.Environment(cr, SUPERUSER_ID, {})
    partners = env['res.partner'].search([])
    for obj in partners:
        if not obj.is_company:
            obj.kw_partner_first_name = obj.name
            obj.kw_is_partner_fullname = True
