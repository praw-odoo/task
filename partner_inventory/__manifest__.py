{
    'name': 'partner_delivery',
    'version': '1.0',
    'category': 'Tools',
    'sequence': 15,
    'description': "helps to set default uom",
    'website': 'http://www.odoo.com/task6',
    'depends': ['contacts','product','sale','sale_management','stock'],
    'data':[
        'views/res_partner_views.xml',
        'security/ir.model.access.csv',
    ],
    'demo': [],
    'installable': True,
    'license': 'LGPL-3'
}