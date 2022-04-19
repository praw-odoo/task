{
    'name':'Website & pay',
    'summary': """ this model is create a pay list in web site views""",
    'description': """
       paylist view in website
    """,
    'author': 'Odoo Ps',
    'version': '1.0.0',

    'depends': ['sale_management','hr','hr_payroll','website'],
    'data' :[
        'views/portal_my_home_inherit.xml',
        'views/hr_payroll_portal_inherit.xml'
        
        ],
    
    
    'installable': True,
    'application': True,
}
