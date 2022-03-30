{
    'name': "Reorder Website",

    'summary': """
        This module is to Reorder Website.
    """,

    'description': """
        Reorder in Website
    """,
    'author': 'Odoo Ps',
    'version': '1.0.0',

    'depends': ['website','sale_management'],

    'data': [
        "views/sale_portal_template.xml",
    ],

    'installable': True,
    'license': 'LGPL-3'
}