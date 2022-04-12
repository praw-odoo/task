{
    'name': "req quo",

    'summary': """
        helps to create quotation from wizard.
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