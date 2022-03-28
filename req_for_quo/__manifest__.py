{
    'name': "req quo",

    'summary': """
        This module is to Reorder Website.
    """,

    'description': """
        Reorder in Website
    """,
    'author': 'Odoo Ps',
    'version': '1.0.0',

    'depends': ['stock','purchase'],

    'data': [
        "wizard/product_template_views.xml",
        "security/ir.model.access.csv"
    ],

    'installable': True,
    'license': 'LGPL-3'
}