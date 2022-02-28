{
    'name': 'task 7',
    'version': '1.0',
    'category': 'Tools',
    'sequence': 15,
    'summary': 'modify task 7',
    'description': "modify task 7",
    'website': 'http://www.odoo.com/task6',
    'depends': ['contacts','product','sale','sale_management','stock'],
    'data':[
        'views/sale_order_zero_stock_approval_views.xml',
        #'security/InternTask_security_views.xml'
    ],
    'demo': [],
    #'installable': True,
    'application': False,
    'auto_install': False,
    'license': 'LGPL-3'
}