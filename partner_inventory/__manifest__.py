{
    'name': 'partner_delivery',
    'version': '1.0',
    'category': 'Tools',
    'sequence': 15,
    'summary': 'modify partner_delivery',
    'description': "modify task 6",
    'website': 'http://www.odoo.com/task6',
    'depends': ['contacts','product','sale','sale_management','stock'],
    'data':[
        'views/res_partner_views.xml',
        
    ],
    'demo': [],
    #'installable': True,
    'application': False,
    'auto_install': False,
    'license': 'LGPL-3'
}