{
    'name': "Birthday Wishes employees",

    'summary': """
        This module is to schedule action for birthday wishes.
    """,

    'description': """
        birthday wishes after interval
    """,
    'author': 'Odoo Ps',
    'version': '1.0.0',

    'depends': ['mail','hr'],

    'data': [
        "data/hr_employee.xml",
        "data/email_template.xml",
        #"security/ir.model.access.csv",
    ],

    'installable': True,
    'license': 'LGPL-3'
}