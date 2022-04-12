{
    'name': "pos_zip",

    'summary': """
        This module is to pos_zip.
    """,

    'description': """
        pos_zip
    """,
    'author': 'Odoo Ps',
    'version': '15.0.1.0.0',

    'depends': ['point_of_sale','contacts','sale_management'],

    'data': [
        "views/pos_order_views.xml"
    ],

    'assets': {
        'point_of_sale.assets': [
            'pos_zip/static/src/js/Screens/ClientListScreen/ClientListScreen.js',
            ],
        'web.assets_qweb': [
        'pos_product_qty/static/src/xml/**/*',
        ],
    },

    'installable': True,
    'license': 'LGPL-3'
}