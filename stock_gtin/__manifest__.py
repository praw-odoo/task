{
    'name': "stock_gtin",

    'description': """
        helps to stock_gtin
    """,

    'author': 'Odoo Ps',
    'version': '1.0.0',

    'depends': ['stock','purchase','sale_management'],

    'data': [
        "data/seq.xml",
        "views/stock_package_type_view.xml",
    ],

    'installable': True,
    'license': 'LGPL-3'
}