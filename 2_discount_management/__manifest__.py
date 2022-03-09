{
    'name': 'credit_limit_customer',
    'version': '1.0',
    'category': 'Tools',
    'sequence': -15,
    'summary': 'modify credit_limit_customer',
    'description': "modify task 6",
    'website': 'http://www.odoo.com/task',
    'depends': ['sale_management', 'account'],
    'data':[
        'views/sale_order_views.xml',
        'views/account_move_line_views.xml',
        'report/sale_order_report.xml'
    ],
    'demo': [],
    #'installable': True,
    'application': False,
    'auto_install': False,
    'license': 'LGPL-3'
}