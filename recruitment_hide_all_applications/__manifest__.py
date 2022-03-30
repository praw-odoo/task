{
    'name': "hide all applications",

    'summary': """
        This module is to hide all applications.
    """,

    'description': """
        hide all applications
    """,
    'author': 'Odoo Ps',
    'version': '1.0.0',

    'depends': ['hr_recruitment'],

    'data': [
        "security/group_hr_recruitment_user_security.xml",
    ],
    'installable': True,
    'license': 'LGPL-3'
}