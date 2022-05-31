{
    #  Information
    'name': 'Library Management System',
    'version': '15.0.1',
    'summary': 'Library Management System',
    'description': """
        Library Management System """,
    'category': 'Sales',

    # Author
    'author': 'Odoo PS',
    'website': 'https://www.odoo.com',

    # Dependency
    'depends': ['stock', 'purchase', 'account', 'sale_management', 'website'],
    
    'data': [
        'security/ir.model.access.csv',
        'report/report_external_standard_layout_template.xml',
        'report/book_detail_template.xml',
        'report/book_detail_report.xml',
        'report/book_issue_detail_template.xml',
        'report/book_issue_detail_report.xml',
        'views/library_book_request_views.xml',
        'views/library_book_stock_views.xml',
        'views/library_book_purchase_views.xml',
        'views/library_book_menus.xml',
        'views/members_registrarion_views.xml',
        'views/book_issue_data_views.xml',
        'views/my_requested_books_template.xml',
        'views/book_details_template.xml',
        'views/view_book_details_template.xml',
        'views/my_issue_books_template.xml',
        'views/my_profile_details_template.xml',
        'views/request_books_template.xml',
        'views/res_users_views.xml',
        'data/navigation.xml',
        'data/mail_template.xml',
        'data/schedule_action.xml',
    ],

    # Other
    'license': 'LGPL-3',
    'installable': True,
    'auto_install': False,
    'application': True,

} 
