from odoo import _, api, fields, models

class sale_order_approval(models.Model):
    _inherit = "sale.order"
    
    zero_stock_approval = fields.Boolean(string='Appoval')