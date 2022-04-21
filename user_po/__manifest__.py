{
    'name': "user_po",

    'summary': """
        This module is to show user_po.
    """,

    'description': """
        custom user_po
    """,
    'author': 'Odoo Ps',
    'version': '15.0.1.0.0',

    'depends': ['stock','purchase_stock', 'purchase'],

    'data': [
        "views/stock_picking_views.xml",
    ],

    'installable': True,
    'license': 'LGPL-3'
}