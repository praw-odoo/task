{
    'name': 'product_stock_picking',
    'version': '1.0',
    'category': 'Tools',
    'sequence': -15,
    'summary': 'modify product_stock_picking',
    'description': "helps to get product",
    'website': 'http://www.odoo.com/task',
    'depends': ['sale_management','account','stock'],
    'data':[
        'views/stock_picking_views.xml',
    ],
    'demo': [],
    'installable': True,
    'license': 'LGPL-3'
}