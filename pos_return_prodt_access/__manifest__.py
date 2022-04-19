{
    'name': "custom module",

    'summary': """
        This module is to show custom module.
    """,

    'description': """
        custom module
    """,
    'author': 'Odoo Ps',
    'version': '15.0.1.0.0',

    'depends': ['point_of_sale'],

    'data': [
        "views/res_config_settings.xml",
        "views/res_users.xml"
    ],

    'installable': True,
    'license': 'LGPL-3'
}