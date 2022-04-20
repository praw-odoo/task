{
    'name': "lot_action",

    'summary': """
        This module is to show lot_action.
    """,

    'description': """
        custom lot_action
    """,
    'author': 'Odoo Ps',
    'version': '15.0.1.0.0',

    'depends': ['stock', 'mrp'],

    'data': [
        "views/mrp_production_views.xml",
        # "views/res_users.xml"
    ],

    'installable': True,
    'license': 'LGPL-3'
}