{
    'name': "Birthday Wishes",

    'summary': """
        This module is to schedule action for birthday wishes.
    """,

    'description': """
        birthday wishes after interval
    """,
    'author': 'Odoo Ps',
    'version': '1.0.0',

    'depends': [],

    'data': [
        "data/cron_demo.xml",
        "security/ir.model.access.csv",
    ],

    'installable': True,
}