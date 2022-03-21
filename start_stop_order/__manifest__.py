{
    'name': "start_stop_order",

    'summary': """
        This module is to start stop timer for manufacturing.
    """,

    'description': """
        This module is to create action in mrp
    """,
    'author': 'Odoo Ps',
    'version': '1.0.0',

    'depends': ['mrp'],

    'data': [
        'wizard/mrp_workorder_view.xml',
    ],

    'installable': True,
}