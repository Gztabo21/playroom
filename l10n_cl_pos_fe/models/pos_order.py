# -*- coding: utf-8 -*-

from odoo import models, fields, api, tools, _
from odoo.exceptions import UserError
from datetime import datetime
from functools import partial
from odoo.tools.float_utils import float_repr, float_round
from html import unescape
from io import BytesIO
from lxml import etree
import base64
import logging
import json
import re
import psycopg2
import pytz

_logger = logging.getLogger(__name__)

class PosOrder(models.Model):
    _name = 'pos.order'
    _inherit = ['pos.order', 'mail.thread', 'mail.activity.mixin']

    l10n_latam_document_number = fields.Char(string="Folio")
    l10n_latam_document_type_id = fields.Many2one('l10n_latam.document.type',
        string='Tipo de Documento',
        readonly=True,
        copy=True,
    )
    signature = fields.Char(
        string="Firma",
    )
    l10n_latam_document_type_id_code = fields.Char(related='l10n_latam_document_type_id.code', string='Codigo de Documento')
    to_ticket = fields.Boolean('To Ticket')

    @api.model
    def _order_fields(self, ui_order):
        fields = super(PosOrder, self)._order_fields(ui_order)
        fields.update({
            'to_ticket': ui_order['to_ticket'] if 'to_ticket' in ui_order else False,
            'l10n_latam_document_type_id': self.env['l10n_latam.document.type'].search([('code', '=', '33')]).id if ui_order['to_invoice'] == True else self.env['l10n_latam.document.type'].search([('code', '=', '39')]).id if ui_order['to_ticket'] == True else False,
            'l10n_latam_document_number': ui_order.get('l10n_latam_document_number', 0)
        })
        return fields

    @api.model
    def _process_order(self, order, draft, existing_order):
        """Create or update an pos.order from a given dictionary.

        :param dict order: dictionary representing the order.
        :param bool draft: Indicate that the pos_order is not validated yet.
        :param existing_order: order to be updated or False.
        :type existing_order: pos.order.
        :returns: id of created/updated pos.order
        :rtype: int
        """
        order = order['data']
        pos_session = self.env['pos.session'].browse(order['pos_session_id'])
        if pos_session.state == 'closing_control' or pos_session.state == 'closed':
            order['pos_session_id'] = self._get_valid_session(order).id

        pos_order = False
        if not existing_order:
            pos_order = self.create(self._order_fields(order))
        else:
            pos_order = existing_order
            pos_order.lines.unlink()
            order['user_id'] = pos_order.user_id.id
            pos_order.write(self._order_fields(order))

        pos_order = pos_order.with_company(pos_order.company_id)
        self = self.with_company(pos_order.company_id)
        self._process_payment_lines(order, pos_order, pos_session, draft)

        if not draft:
            try:
                pos_order.action_pos_order_paid()
            except psycopg2.DatabaseError:
                # do not hide transactional errors, the order(s) won't be saved!
                raise
            except Exception as e:
                _logger.error('Could not fully process the POS Order: %s', tools.ustr(e))
            pos_order._create_order_picking()
            pos_order._compute_total_cost_in_real_time()

        if (pos_order.to_invoice or pos_order.to_ticket) and pos_order.state == 'paid':
            pos_order.action_pos_order_invoice()

        return pos_order.id

    def _prepare_invoice_vals(self):
        res = super(PosOrder, self)._prepare_invoice_vals()
        res['l10n_latam_document_type_id'] = self.l10n_latam_document_type_id.id
        return res

    @api.model
    def create_from_ui(self, orders, draft=False):
        """ Create and update Orders from the frontend PoS application.

        Create new orders and update orders that are in draft status. If an order already exists with a status
        diferent from 'draft'it will be discareded, otherwise it will be saved to the database. If saved with
        'draft' status the order can be overwritten later by this function.

        :param orders: dictionary with the orders to be created.
        :type orders: dict.
        :param draft: Indicate if the orders are ment to be finalised or temporarily saved.
        :type draft: bool.
        :Returns: list -- list of db-ids for the created and updated orders.
        """
        order_ids = []
        for order in orders:
            existing_order = False
            if 'server_id' in order['data']:
                existing_order = self.env['pos.order'].search(['|', ('id', '=', order['data']['server_id']), ('pos_reference', '=', order['data']['name'])], limit=1)
            if (existing_order and existing_order.state == 'draft') or not existing_order:
                order_ids.append(self._process_order(order, draft, existing_order))

        return self.env['pos.order'].search_read(domain=[('id', 'in', order_ids)], fields=['id', 'pos_reference', 'account_move'])

    @api.model
    def get_next_ticket_number(self, session):
        folio = False
        last_invoice = self.env['account.move'].search([('l10n_latam_document_type_id_code', '=', 39), ('state', 'not in', [])], order="id desc")
        if last_invoice:
            folio = int(last_invoice[0].l10n_latam_document_number) + 1
        return str(folio)

    @api.model
    def get_next_invoice_number(self):
        folio = False
        last_invoice = self.env['account.move'].search([('l10n_latam_document_type_id_code', '=', 33)], order="id desc")
        if last_invoice:
            folio = int(last_invoice[0].l10n_latam_document_number) + 1
        return str(folio)
