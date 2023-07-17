{
    'name': 'Refund Accounts',
    'name_vi_VN': 'Tài khoản hoàn tiền',
    'version': '1.0',
    'category': 'Accounting',
    'author': "JIMMY ARAUJO",
    'summary': 'Cuentas dedevoluciones para ingresos y gastos',
    'description': """
Funciones
============
* De manera predeterminada, Odoo contabiliza los montos en la cuenta original de ingresos/gastos al validar las facturas de devolucion.
* Este módulo le permitirá especificar diferentes cuentas para la devolución de ingresos y gastos en las categorias de los prodcutos.



""",
    'description_vi_VN': """


""",
    'depends': ['account'],
    'data': [
        'views/product_category_view.xml',
        'views/product_template_view.xml',
    ],
    'images' : ['static/description/main_screenshot.png'],
    'installable': True,
    'application': False,
    'auto_install': True,
    'price': 18.9,
    'currency': 'EUR',
    'license': 'OPL-1',
}
