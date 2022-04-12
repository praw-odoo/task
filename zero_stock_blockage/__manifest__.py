{
    'name': 'zero_stock_blockage',
    'version': '1.0',
    'category': 'Tools',
    'sequence': 15,
    'description': "helps to show field only to admo=in",
    'website': 'http://www.odoo.com/task6',
    'depends': ['contacts','product','sale','sale_management','stock'],
    'data':[
        'views/sale_order_views.xml',
        #'security/sale_order_security_views.xml'
    ],
    'demo': [],
    'installable': True,
    'license': 'LGPL-3'
}