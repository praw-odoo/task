{
    'name': "contracts",

    'summary': """
        This module is to Traceback Field in mrp.
    """,

    'description': """
        Traceback Field in mrp
    """,
    'author': 'Odoo Ps',
    'version': '1.0.0',

    'depends': ['sale_management','contacts'],

    'data': [
        "security/ir.model.access.csv",
        "views/res_partner_views.xml",
        "views/contract_price_details_views.xml",
        
    ],
    'installable': True,
    'license': 'LGPL-3'
}