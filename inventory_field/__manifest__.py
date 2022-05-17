{
    'name': "inventory_field",

    'description': """
        helps to inventory_field
    """,
    'author': 'Odoo Ps',
    'version': '1.0.0',

    'depends': ['stock'],

    'data': [
        # "views/stock_picking_type_views.xml",
        "views/stock_move_line_views.xml",
        # "views/templates.xml",
    ],
    'installable': True,
    'license': 'LGPL-3'
}