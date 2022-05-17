import math, json
from odoo import api,models,fields
from datetime import datetime

class PurchaseOrder(models.Model):
    _inherit = "purchase.order"

    invoice_cash_rounding_id = fields.Many2one('account.cash.rounding',string='Cash Rounding Method')
    
    @api.depends('order_line.price_total')
    def _amount_all(self):
        res = super()._amount_all()
        for order in self:
            if order.invoice_cash_rounding_id.rounding_method =="UP":
                order.amount_total = math.ceil(order.amount_total)
            elif order.invoice_cash_rounding_id.rounding_method =="DOWN":
                order.amount_total = math.floor(order.amount_total)
        order.update({
            'amount_total' : order.amount_total,
        })

    @api.onchange('order_line','invoice_cash_rounding_id')
    def _onchange_amount_all(self):
        rounding_product_id = self.env.ref('po_roundingcash.product_product_round_off')
        for order in self:
            def _round_ceil(self):
                if order.order_line.taxes_id:
                    if order.invoice_cash_rounding_id.rounding >= 1:
                        temp2 = math.ceil(order.amount_total) - order.amount_total
                        order.amount_tax += temp2
                    else:
                        check = (order.amount_total * 100)%10
                        if check >= 5: order.amount_tax += round(order.amount_total, 1) - order.amount_total
                        else: order.amount_tax += round(order.amount_total, 1) - order.amount_total + 0.1
                else:
                    if order.invoice_cash_rounding_id.rounding >= 1: order.amount_total = math.ceil(order.amount_total)
                    else:
                        check = (order.amount_total * 100)%10
                        if check >= 5: order.amount_total = round(order.amount_total, 1)
                        else: order.amount_total = round(order.amount_total, 1) + 0.1

            def _round_floor(self):
                if order.order_line.taxes_id:
                    if order.invoice_cash_rounding_id.rounding >= 1:
                        order.amount_tax += math.floor(order.amount_total) - order.amount_total
                    else:
                        check = (order.amount_total * 100)%10
                        if check >= 5: order.amount_tax += round(order.amount_total, 1) - order.amount_total - 0.1
                        else: order.amount_tax += round(order.amount_total, 1) - order.amount_total
                else:
                    if order.invoice_cash_rounding_id.rounding >= 1:
                        order.amount_total = math.floor(order.amount_total)
                    else:
                        check = (order.amount_total * 100)%10
                        if check >= 5: order.amount_total = round(order.amount_total, 1) - 0.1
                        else: order.amount_total = round(order.amount_total, 1)

            def create_line_in_po(po_val):
                po_line_vals ={
                    'product_id': rounding_product_id.id,
                    'order_id': order._origin.id,
                    'name': order.invoice_cash_rounding_id.name,
                    'product_qty': 1,
                    'price_unit': po_val,
                    'price_subtotal': po_val,
                    'display_type': False,
                    'product_uom': 1,
                    'date_planned': datetime.now(),
                }
                order.order_line = [(0,0,po_line_vals)]

            def _round_ceil_line(self):
                temp1 = 0
                if order.invoice_cash_rounding_id.rounding >= 1:
                    temp1 = math.ceil(order.amount_total) - order.amount_total
                elif order.invoice_cash_rounding_id.rounding >= 0.1 and order.invoice_cash_rounding_id.rounding < 1 and order.order_line.price_unit > math.floor(order.order_line.price_unit):
                    temp1 = math.floor(order.amount_total) - order.amount_total
                    check1 = (order.amount_total * 100)%10
                    temp1 += check1*(0.1) + 0.1
                create_line_in_po(temp1)
                
            def _round_floor_line(self):
                temp1 = 0
                if order.invoice_cash_rounding_id.rounding >= 1:
                    temp1 = math.floor(order.amount_total) - order.amount_total
                elif order.invoice_cash_rounding_id.rounding >= 0.1 and order.invoice_cash_rounding_id.rounding < 1 and order.order_line.price_unit > math.floor(order.order_line.price_unit):
                    temp1 = math.floor(order.amount_total) - order.amount_total
                    check1 = (order.amount_total * 100)%10
                    temp1 += check1*(0.1) - 0.1
                create_line_in_po(temp1)
                
            for virtualid in order.order_line:
                if virtualid.product_id.id == rounding_product_id.id:
                    order.order_line -= virtualid
            if order.order_line.product_id:
                if order.invoice_cash_rounding_id.strategy == "biggest_tax":
                    if order.invoice_cash_rounding_id.rounding_method =="UP": _round_ceil(self)
                    elif order.invoice_cash_rounding_id.rounding_method =="DOWN":_round_floor(self)
                    elif order.invoice_cash_rounding_id.rounding_method =="HALF-UP":
                        temp = math.floor(order.amount_total) + 0.50
                        if order.amount_total >= temp: _round_ceil(self)
                        elif order.amount_total < temp: _round_floor(self)
                elif order.invoice_cash_rounding_id.strategy == "add_invoice_line":
                    if order.invoice_cash_rounding_id.rounding_method =="UP": _round_ceil_line(self)
                    elif order.invoice_cash_rounding_id.rounding_method =="DOWN": _round_floor_line(self)
                    elif order.invoice_cash_rounding_id.rounding_method =="HALF-UP":
                        temp = math.floor(order.amount_total) + 0.50
                        if order.amount_total >= temp: _round_ceil_line(self)
                        elif order.amount_total < temp: _round_floor_line(self)
