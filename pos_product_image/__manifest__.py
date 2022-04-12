{
    'name': "pos_customer",

    'summary': """
        This module is to pos_customer.
    """,

    'description': """
        pos_customer
    """,
    'author': 'Odoo Ps',
    'version': '15.0.1.0.0',

    'depends': ['point_of_sale'],

    'data': [
    ],

    'qweb': [
        'static/src/xml/productimg.xml',
    ],

    'assets': {
        'point_of_sale.assets': [
            'pos_customer/static/src/js/productimg.js',
            ]
        },

    'installable': True,
    'license': 'LGPL-3'
}