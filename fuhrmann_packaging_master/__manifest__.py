# -*- coding: utf-8 -*-

{
    'name': "Fuhrmann Packagin Master",
    'summary': """Additional fields on Product Packaging""",
    'description': """Task ID - 2858332, Additional fields on Product Packaging""",
    "author": "OdooPS",
    "website": "http://www.odoo.com",
    "category": "Customizations",
    "version": "15.0.1.0.0",
    "license": "LGPL-3",
    'depends': ['product', 'stock'],
    'data': [
        'data/sequence.xml',
        'views/product_packaging_views.xml',
        'views/stock_package_type.xml'
    ],
    'pre_init_hook': '_create_barcode_sequence',
    'application': False,
    'installable': True,
    'auto_install': False,
}
