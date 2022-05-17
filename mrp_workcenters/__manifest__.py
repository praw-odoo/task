{
    'name': "inventory_field",

    'description': """
        helps to inventory_field
    """,
    'author': 'Odoo Ps',
    'version': '1.0.0',

    'depends': ['mrp'],

    'data': [
        "views/mrp_routing_workcenter_view.xml",
    ],
    'installable': True,
    'license': 'LGPL-3'
}