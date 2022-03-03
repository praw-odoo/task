from odoo import api, models, fields
from odoo.exceptions import UserError

class AccountMove(models.Model):
    _inherit = "account.move"

    @api.constrains("amount_total")
    def _check_total_invoice(self):
        total_recivable = self.amount_total + self.partner_id.credit

        if total_recivable > self.partner_id.credit_limit:
            raise UserError("Total receivable can't greater than credit limit")