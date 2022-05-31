# -*- coding: utf-8 -*-
{
    'name': "OBS Asphericon Valuation",

    'summary': """OBS Asphericon Valuation""",

    'description': """
        Module for OBS Asphericon Valuation
        task:2678906
    """,
    'author': "Odoo Business Solutions",
    'website': "https://www.odoo.com",
    'category': 'stock',
    'version': '0.1',
    'depends': ['stock'],
    'data': [
        'security/ir.model.access.csv',
        'security/security.xml',
        'views/stock_valuation_views.xml',
        'views/stock_quant_views.xml',
        'views/product_views.xml',
    ],
}
