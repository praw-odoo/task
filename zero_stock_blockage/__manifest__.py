{
    'name': 'zero_stock_blockage',
    'version': '1.0',
    'category': 'Tools',
    'sequence': 15,
    'summary': 'modify zero_stock_blockage',
    'description': "modify task 7",
    'website': 'http://www.odoo.com/task6',
    'depends': ['contacts','product','sale','sale_management','stock'],
    'data':[
        'views/sale_order_views.xml',
        #'security/sale_order_security_views.xml'
    ],
    'demo': [],
    #'installable': True,
    'application': False,
    'auto_install': False,
    'license': 'LGPL-3'
}