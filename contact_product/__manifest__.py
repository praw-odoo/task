{
    'name': "Birthday Wishes employees",

    'description': """
        This module helps to assign sequence to product
    """,

    'author': 'Odoo Ps',
    'version': '1.0.0',

    'depends': ['sale_management', 'contacts'],

    'data': [
        'data/data_product_seq.xml',
        'views/res_partner_views.xml',
        #'views/product_template_views.xml',
        'views/product_category_views.xml',
    ],

    'installable': True,
    'license': 'LGPL-3'
}