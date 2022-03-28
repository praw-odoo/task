{
    'name': 'delivery_shipping',
    'version': '1.0',
    'category': 'Tools',
    'sequence': 15,
    'summary': 'modify delivery_shipping',
    'description': "modify task 6",
    'website': 'http://www.odoo.com/task6',
    'depends': ['contacts','product','sale','sale_management','stock'],
    'data':[
        'views/res_partner_views.xml',
        'views/sale_order_views.xml',
        'views/stock_picking_views.xml',
        #'views/res_partner_number_of_days_views.xml'
        #'security/InternTask_security_views.xml'
    ],
    'demo': [],
    'installable': True,
    'license': 'LGPL-3'
}