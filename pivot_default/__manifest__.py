{
    'name': "stock_gtin",

    'description': """
        helps to stock_gtin
    """,
    'author': 'Odoo Ps',
    'version': '1.0.0',

    'depends': ['purchase'],

    'data': [
        "views/pivot_default_view.xml",
    ],
    'installable': True,
    'license': 'LGPL-3'
}