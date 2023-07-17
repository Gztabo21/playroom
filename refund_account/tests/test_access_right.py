from odoo.tests import tagged
from odoo.exceptions import AccessError

from .common import Common

@tagged('post_install', '-at_install', 'access_rights')
class TestAccessRight(Common):
    
    @classmethod
    def setUpClass(cls):
        super().setUpClass()
        cls.user = cls.env.ref('base.user_admin')

    def test_access_right_product_category(self):
        """INPUT:
            user:
                Invoicing: Billing Administrator
                Administration: Setting
                Access Right: Show Accounting Features - Readonly
            OUTPUT: user can create, write product category
        """
        self.user.write({
            'groups_id': [(6, 0, [self.env.ref('account.group_account_manager').id,
                                    self.env.ref('account.group_account_readonly').id,
                                    self.env.ref('base.group_system').id])]
            })

        self.product_category.with_user(self.user).write({
            'property_account_income_refund_categ_id': self.account_refund_income_product.id,
            'property_account_expense_refund_categ_id':self.account_refund_expense_product.id,         
            })
        
        self.env['product.category'].with_user(self.user).create({
            'name': 'Category 1',
            'property_account_income_refund_categ_id': self.account_refund_income_product.id,
            'property_account_expense_refund_categ_id': self.account_refund_expense_product.id,
            })

    def test_access_right_product_1(self):
        """INPUT: 
            user: 
                Invoicing: Billing Administrator
                Administration: Access Rights
                Access Right: Show Accounting Features - Readonly
            OUTPUT: user can create, write product
        """
        self.user.write({
            'groups_id': [(6, 0, 
                        [self.env.ref('account.group_account_manager').id,
                         self.env.ref('account.group_account_readonly').id,
                         self.env.ref('base.group_erp_manager').id])]
            })

        self.product_product.with_user(self.user).write({
                'property_account_income_refund_id': self.account_refund_income_product.id,
                'property_account_expense_refund_id': self.account_refund_expense_product.id,
            })

        self.env['product.template'].with_user(self.user).create({
                'name' : ' Product 1',
                'property_account_income_refund_id': self.account_refund_income_product.id,
                'property_account_expense_refund_id': self.account_refund_expense_product.id,            
            })

    def test_access_right_product_2(self):
        """INPUT:
            user: 
                Invoicing: Billing
                Administration: Setting
                Access Right: Show Accounting Features - Readonly
            OUTPUT: user can create/write product
        """
        self.user.write({
            'groups_id': [(6, 0, [self.env.ref('account.group_account_invoice').id,
                                    self.env.ref('account.group_account_readonly').id,
                                    self.env.ref('base.group_system').id])]
            })
        
        self.product_product.with_user(self.user).write({
                'property_account_income_refund_id': self.account_refund_income_product.id,
                'property_account_expense_refund_id': self.account_refund_expense_product.id,
            })
        
        self.env['product.template'].with_user(self.user).create({
                'name' : ' Product 1',
                'property_account_income_refund_id': self.account_refund_income_product.id,
                'property_account_expense_refund_id': self.account_refund_expense_product.id,            
            })

    def test_access_right_product_3(self):
        """INPUT:
            user: 
                Invoicing: Billing
                Administration: Access Rights
                Access Right: Show Accounting Features - Readonly
            OUTPUT: user can not create/write product
        """
        self.user.write({
            'groups_id': [(6, 0, [self.env.ref('account.group_account_invoice').id,
                                    self.env.ref('account.group_account_readonly').id,
                                    self.env.ref('base.group_erp_manager').id])]
            })

        with self.assertRaises(AccessError):
            self.product_product.with_user(self.user).write({
                'property_account_income_refund_id': self.account_refund_income_product.id,
                'property_account_expense_refund_id': self.account_refund_expense_product.id,
                })
        with self.assertRaises(AccessError):
            self.env['product.template'].with_user(self.user).create({
                'name' : ' Product 1',
                'property_account_income_refund_id': self.account_refund_income_product.id,
                'property_account_expense_refund_id': self.account_refund_expense_product.id,
                })
