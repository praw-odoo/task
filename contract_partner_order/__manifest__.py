{
    'name': "contract partner order",

    'description': """
        make field price in sale order according to define in contacts
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