{
    'name': "Birthday Wishes employees",

    'description': """
        This module is schedule action for birthday wishes of employees
    """,

    'author': 'Odoo Ps',
    'version': '1.0.0',

    'depends': ['mail','hr'],

    'data': [
        "data/hr_employee.xml",
        "data/email_template.xml",
        # "security/ir.model.access.csv",
    ],

    'installable': True,
    'license': 'LGPL-3'
}