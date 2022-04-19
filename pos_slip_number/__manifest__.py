{
    'name': "pos_slip_number",

    'summary': """
        This module is to add sequence.
    """,

    'description': """
        sequence order
    """,
    'author': 'Odoo Ps',
    'version': '15.0.1.0.0',

    'depends': ['point_of_sale'],

    'data': [
        "data/seq.xml",
        "views/pos_order_views.xml"
    ],

    'assets': {
        'point_of_sale.assets': [
            'pos_slip_number/static/src/js/models.js',
            ],
        'web.assets_qweb': [
        'pos_slip_number/static/src/xml/Screens/ReceiptScreen/OrderReceipt.xml',
        ],
    },

    'installable': True,
    'auto_install': True,
    'license': 'LGPL-3'
}