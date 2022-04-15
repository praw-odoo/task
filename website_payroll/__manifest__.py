{
    'name': "sale_invoice_button",

    'summary': """
        This module is to show payslip in website.
    """,

    'description': """
        sale_invoice_button
    """,
    'author': 'Odoo Ps',
    'version': '15.0.1.0.0',

    'depends': ['website','hr_payroll','hr','portal'],

    'data': [
        "views/portal_templates.xml",
        "views/render_payslip_list.xml",
        "views/payslip_template.xml"
    ],

    'installable': True,
    'license': 'LGPL-3'
}