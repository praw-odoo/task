{
    'name': "po_cash_rounding",

    'description': """
        helps to po_cash_rounding
    """,
    'author': 'Odoo Ps',
    'version': '1.0.0',

    'depends': ['account','purchase','account_accountant'],

    'data': [
        "views/purchase_order_voews.xml",
        "views/purchase_order_line_view.xml",
    ],
    'installable': True,
    'license': 'LGPL-3'
}