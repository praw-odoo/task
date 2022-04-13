{
    'name': "pos_product_qty",

    'summary': """
        This module is to add and subtract pos product qty.
    """,

    'description': """
        pos_product_qty
    """,
    'author': 'Odoo Ps',
    'version': '15.0.1.0.0',

    'depends': ['point_of_sale'],

    'data': [
    ],

    'installable': True,
    'auto_install': True,

    'assets': {
        'point_of_sale.assets': [
            'pos_product_qty/static/src/js/ProductScreen/ProductItem.js',
            'pos_product_qty/static/src/css/button.css',
            ],
        'web.assets_qweb': [
        'pos_product_qty/static/src/xml/**/*',
        ],
    },

    'license': 'LGPL-3'
}