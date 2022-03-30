{
    'name': "inventory customization",

    'summary': """
        This module is to inventory customization.
    """,

    'description': """
        inventory customization
    """,
    'author': 'Odoo Ps',
    'version': '1.0.0',

    'depends': ['stock'],

    'data': [
        "views/res_config_setting_views.xml",
    ],
    'installable': True,
    'license': 'LGPL-3'
}