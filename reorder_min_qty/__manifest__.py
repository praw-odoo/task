{
    'name': "stock_gtin",

    'description': """
        helps to stock_gtin
    """,
    'author': 'Odoo Ps',
    'version': '1.0.0',

    'depends': ['stock','purchase','sale_management'],

    'data': [
        "views/stock_warhouse_orderpoint_view.xml",
    ],
    'installable': True,
    'license': 'LGPL-3'
}