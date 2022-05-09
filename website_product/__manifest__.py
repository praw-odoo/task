{
    'name': "website_product",

    'summary': """
        This module is to show website_product.
    """,

    'description': """
        website_product
    """,
    'author': 'Odoo Ps',
    'version': '15.0.1.0.0',

    'depends': ['website','sale_management','website_slides','website_sale'],

    'data': [
    "views/product_template_views.xml",
    "views/template.xml"
    ],

    'installable': True,
    'license': 'LGPL-3'
}