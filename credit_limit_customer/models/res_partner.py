#from argparse import _MutuallyExclusiveGroup

from odoo import api, fields, models
from odoo.exceptions import UserError


class ResPartner(models.Model):
    _inherit="res.partner"

    # credit_limit=fields.Integer(string="Credit Limit")
    # total_receivable=fields.Integer(string="total Receivable")

    # @api.onchange("credit_limit","credit")
    # def _onchange_credit_limit(self):
    #     print("\n\n\n\n\ hello ")
    #     if self.credit > self.credit_limit:
    #         self.sale_order_count = None
    #         self.total_invoiced = None
    #         raise UserError(("Recivable price cannot be greater than credit limit."))
            
            