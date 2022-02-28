from odoo import _, api, fields, models

class SaleOrder(models.Model):
    _inherit = "sale.order"
    
    zero_stock_approval = fields.Boolean(string='Appoval')

    def _approval(self):
        if self.env.uid == self.parent_id.user_id.id:
            self.zero_stock_approval = True