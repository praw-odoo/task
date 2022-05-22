{
    'name': "po_roundingcash",

    'description': """
        helps to po_roundingcash
    """,
    'author': 'Odoo Ps',
    'version': '1.0.0',

    'depends': ['account_accountant','purchase','stock'],

    'data': [
        "data/product_data.xml",
        "views/purchase_order_view.xml",
    ],
    'installable': True,
    'license': 'LGPL-3'
}