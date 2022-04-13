{
    'name': 'credit limit customer',
    'version': '1.0',
    'category': 'Tools',
    'sequence': 15,
    'description': "this module helps to calculate secound discount on product",
    'website': 'http://www.odoo.com/task',
    'depends': ['sale_management', 'account'],
    'data':[
        'views/sale_order_views.xml',
        'views/account_move_line_views.xml',
        'report/sale_order_report.xml',
        'report/account_order_report.xml',
    ],
    'installable': True,
    'license': 'LGPL-3'
}