{
    'name': "sale_invoice_button",

    'summary': """
        This module is to product from button in account move line
    """,

    'description': """
        sale_invoice_button
    """,
    'author': 'Odoo Ps',
    'version': '15.0.1.0.0',

    'depends': ['sale_management','account','account_accountant'],

    'data': [
        "security/ir.model.access.csv",
        "views/product_template_views.xml",
        "wizard/product_template_views.xml",
    ],

    'installable': True,
    'license': 'LGPL-3'
}