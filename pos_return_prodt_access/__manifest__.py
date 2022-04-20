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
        "views/pos_config_views.xml",
        "views/res_users.xml"
    ],

    'assets': {
        'point_of_sale.assets': [
            'pos_return_prodt_access/static/src/js/Screens/ProductScreen.js',
            ],
        'web.assets_qweb': [
        'pos_return_prodt_access/static/src/xml/**/*',
        ],
    },

    'installable': True,
    'license': 'LGPL-3'
}