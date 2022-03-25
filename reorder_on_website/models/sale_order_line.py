from odoo import api, models, fields

class SaleOrderLine(models.Model):
    _inherit = "sale.order.line"

    def action_reorder(self,name):
        pass
