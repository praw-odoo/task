from odoo import api, fields, models
from odoo.exceptions import UserError

class SaleOrder(models.Model):
    _inherit = "sale.order"

    @api.constrains("amount_total")
    def _check_total_sale(self):
        print("\n\n\n\n ",self.tax_totals_json)
        total_amount = self.amount_total + self.partner_id.credit
        if total_amount > self.partner_id.credit_limit:
            raise UserError("Total can't greater than credit limit")