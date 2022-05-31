{
    'name': "product_supplier",

    'description': """
        helps to product_supplier
    """,

    'author': 'Odoo Ps',
    'version': '1.0.0',

    'depends': ['stock','purchase'],

    'data': [
        "views/product_supplierinfo.xml",
    ],

    'installable': True,
    'license': 'LGPL-3'
}