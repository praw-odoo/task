{
    'name': 'contact_product',
    'version': '1.0',
    'category': 'Tools',
    'sequence': -15,
    'summary': 'modify contact_product',
    'description': "modify task contact_product",
    'website': 'http://www.odoo.com/task',
    'depends': ['sale_management', 'contacts'],
    'data':[
        'data/data_product_seq.xml',
        'views/res_partner_views.xml',
        #'views/product_template_views.xml',
        'views/product_category_views.xml',
    ],
    'demo': [],
    'installable': True,
    'application': False,
    'auto_install': False,
    'license': 'LGPL-3'
}