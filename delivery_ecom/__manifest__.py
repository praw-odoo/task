{
    'name': "delivery_ecom",

    'summary': """
        This module is to create field in contact.
    """,

    'description': """
        This module is to create field in contact
    """,
    'author': 'Odoo Ps',
    'version': '1.0.0',

    'depends': ['sale_management', 'website', 'website_sale'],

    'data': [
        'views/res_partner_views.xml',
    ],

    'installable': True,
}