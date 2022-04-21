{
    'name': "bom_schedule_activity",

    'summary': """
        This module is to show bom_schedule_activity.
    """,

    'description': """
        custom bom_schedule_activity
    """,
    'author': 'Odoo Ps',
    'version': '15.0.1.0.0',

    'depends': ['mrp'],

    'data': [
        "views/mrp_bom_views.xml",
    ],

    'installable': True,
    'license': 'LGPL-3'
}