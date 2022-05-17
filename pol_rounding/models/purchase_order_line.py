import json
from odoo import api,models,fields
from odoo.exceptions import UserError

class PurchaseOrderLine(models.Model):
    _inherit = "purchase.order.line"

    @api.depends('product_qty', 'price_unit', 'taxes_id')
    def _compute_amount(self):
        print("\n\n in _compute_amount_compute_amount","order_id.round_of_cash")
        res = super()._compute_amount()
        if not res['taxes']:
            if order_id.round_of_cash.strategy == "biggest_tax":
                if order.round_of_cash.rounding_method =="UP": 
                        taxes['total_included'] = math.ceil(taxes['total_included'])
                elif order.round_of_cash.rounding_method =="DOWN":
                        taxes['total_included'] = math.floor(taxes['total_included'])
                elif order.round_of_cash.rounding_method =="HALF-UP":
                        temp = math.floor(i['tax_amount']) + 0.50
                        if i['tax_amount'] >= temp:
                            taxes['total_included'] = math.ceil(taxes['total_included'])
                        elif i['tax_amount'] < temp:
                            taxes['total_included'] = math.floor(taxes['total_included'])
        return res