{
    'name': "inventory_field",

    'description': """
        helps to inventory_field
    """,
    'author': 'Odoo Ps',
    'version': '1.0.0',

    'depends': ['account','purchase','account_accountant'],

    'data': [
        "data/product_data.xml",
        "views/purchase_order_view.xml",
    ],
    'installable': True,
    'license': 'LGPL-3'
}