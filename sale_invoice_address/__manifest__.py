{
    'name': "sale_invoice_address",

    'description': """
        helps to sale_invoice_address
    """,

    'author': 'Odoo Ps',
    'version': '1.0.0',

    'depends': ['contacts','account','sale_management','stock'],

    'data': [
        "views/res_partner.xml",
    ],

    'installable': True,
    'license': 'LGPL-3'
}