{
    'name': "inventory customization",

    'description': """
        helps to add followers from particular group
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