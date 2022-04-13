{
    'name': 'delivery_shipping',
    'version': '1.0',
    'category': 'Tools',
    'sequence': 15,
    'description': "this module helps to set last date of selivery from starting date and number of days",
    'website': 'http://www.odoo.com/task6',
    'depends': ['contacts','product','sale','sale_management','stock'],
    'data':[
        'views/res_partner_views.xml',
        'views/sale_order_views.xml',
        'views/stock_picking_views.xml',
    ],
    'demo': [],
    'installable': True,
    'license': 'LGPL-3'
}