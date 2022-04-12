{
    'name': 'credit_limit_customer',
    'version': '1.0',
    'category': 'Tools',
    'sequence': 15,
    'description': " this module create modify credit_limit_customer",
    'website': 'http://www.odoo.com/task',
    'depends': ['project', 'sale_management', 'account', 'contacts'],
    'data':[
        'views/res_partner_views.xml',
    ],
    'installable': True,
    'license': 'LGPL-3'
}