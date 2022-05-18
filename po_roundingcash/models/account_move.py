import math, json
from odoo import api,models,fields

class AccountMove(models.Model):
    _inherit = "account.move"

    @api.model
    def create(self, vals):
        res = super().create(vals)
        print("\n\n vals",vals)
        return res