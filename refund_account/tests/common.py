from odoo.tests import SavepointCase, tagged

@tagged('post_install', '-at_install')
class Common(SavepointCase):

    @classmethod
    def setUpClass(cls):
        super(SavepointCase, cls).setUpClass()
        cls.env = cls.env(context=dict(cls.env.context, tracking_disable=True))
        cls.partner = cls.env.ref('base.res_partner_1')
        cls.product_category = cls.env.ref('product.product_category_5')
        cls.product_delivery = cls.env.ref('product.product_delivery_01')
        cls.product_product = cls.env.ref('product.product_product_25')
        cls.product_category_account_income =  cls.product_category.property_account_income_categ_id
        cls.product_category_account_expense =  cls.product_category.property_account_expense_categ_id
        cls.account_refund_income_category = cls.env['account.account'].create({
            'name': 'Redund Income Category',
            'code': 52111,
            'user_type_id': cls.env.ref('account.data_account_type_revenue').id
        })
        cls.account_refund_expense_category = cls.env['account.account'].create({
            'name': 'Redund Expense Category',
            'code': 62111,
            'user_type_id': cls.env.ref('account.data_account_type_expenses').id
        })
        cls.account_refund_income_product = cls.env['account.account'].create({
            'name': 'Redund Income Product',
            'code': 52112,
            'user_type_id': cls.env.ref('account.data_account_type_revenue').id
        })
        cls.account_refund_expense_product = cls.env['account.account'].create({
            'name': 'Redund Expense Product',
            'code': 62112,
            'user_type_id': cls.env.ref('account.data_account_type_expenses').id
        })
        cls.product_category.write({
            'property_account_income_refund_categ_id': cls.account_refund_income_category,
            'property_account_expense_refund_categ_id': cls.account_refund_expense_category
        })
        cls.product_delivery.write({
            'property_account_income_refund_id': cls.account_refund_income_product,
            'property_account_expense_refund_id': cls.account_refund_expense_product
        })
