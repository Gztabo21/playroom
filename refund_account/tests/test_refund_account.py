from odoo import fields
from odoo.tests import tagged

from .common import Common
@tagged('post_install', '-at_install')
class TestAccount(Common):

    @classmethod
    def init_invoice(cls, move_type):
        move = cls.env['account.move'].create({
            'move_type': move_type,
            'invoice_date': fields.Date.from_string('2022-02-01'),
            'partner_id': cls.partner.id,
            'invoice_line_ids': [(0, 0, {
                'product_id': cls.product_delivery.id,
            })],
        })
        return move

    def test_not_config_refund_account(self):
        self.product_category.write({
            'property_account_income_refund_categ_id': False,
            'property_account_expense_refund_categ_id': False
        })
        self.product_delivery.write({
            'property_account_income_refund_id': False,
            'property_account_expense_refund_id': False
        })
        invoice = self.init_invoice('out_refund')
        self.assertEqual(invoice.invoice_line_ids[0].account_id, self.product_category_account_income)

    def test_onchange_refund_account_category(self):
        self.product_delivery.write({
            'property_account_income_refund_id': False,
            'property_account_expense_refund_id': False
        })
        invoice = self.init_invoice('out_refund')
        self.assertEqual(invoice.invoice_line_ids[0].account_id, self.account_refund_income_category)
        self.assertIn(invoice.invoice_line_ids.mapped('account_id'), self.account_refund_income_category)
        invoice = self.init_invoice('in_refund')
        self.assertEqual(invoice.invoice_line_ids[0].account_id, self.account_refund_expense_category)
        self.assertIn(invoice.invoice_line_ids.mapped('account_id'), self.account_refund_expense_category)

    def test_onchange_refund_account_product(self):
        invoice = self.init_invoice('out_refund')
        self.assertEqual(invoice.invoice_line_ids[0].account_id, self.account_refund_income_product)
        self.assertIn(invoice.invoice_line_ids.mapped('account_id'), self.account_refund_income_product)
        invoice = self.init_invoice('in_refund')
        self.assertEqual(invoice.invoice_line_ids[0].account_id, self.account_refund_expense_product)
        self.assertIn(invoice.invoice_line_ids.mapped('account_id'), self.account_refund_expense_product)

    def test_add_credit_note(self):
        invoice = self.init_invoice('out_invoice')
        invoice._post()
        wizard = self.env['account.move.reversal'].with_context(active_model="account.move", active_ids=invoice.ids).create({
            'refund_method': 'cancel'
        })
        refund = wizard.reverse_moves()
        reverse_move = self.env['account.move'].browse(refund['res_id'])
        self.assertEqual(invoice.payment_state, 'reversed')
        self.assertEqual(reverse_move.invoice_line_ids[0].account_id, self.account_refund_income_product)
        self.assertIn(reverse_move.invoice_line_ids.mapped('account_id'), self.account_refund_income_product)

    def test_add_credit_note_2(self):
        invoice = self.init_invoice('in_invoice')
        invoice._post()
        wizard = self.env['account.move.reversal'].with_context(active_model="account.move", active_ids=invoice.ids).create({
            'refund_method': 'cancel'
        })
        refund = wizard.reverse_moves()
        reverse_move = self.env['account.move'].browse(refund['res_id'])
        self.assertEqual(invoice.payment_state, 'reversed')
        self.assertEqual(reverse_move.invoice_line_ids[0].account_id, self.account_refund_expense_product)
        self.assertIn(reverse_move.invoice_line_ids.mapped('account_id'), self.account_refund_expense_product)
