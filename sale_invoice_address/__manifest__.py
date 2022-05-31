{
    "name": "sale_invoice_address",
    "description": """
        helps to set default addresses(invoice and shipping address) in sale order according
        to the booelan ticked in partner
    """,
    "author": "Odoo Ps",
    "version": "1.0.0",
    "depends": ["contacts", "account", "sale_management", "stock"],
    "data": ["views/res_partner.xml"],
    "installable": True,
    "license": "LGPL-3",
}
