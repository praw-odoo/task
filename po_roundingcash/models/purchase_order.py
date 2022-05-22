import math, json
from odoo import api,models,fields
from datetime import datetime

class PurchaseOrder(models.Model):
    _inherit = "purchase.order"

    invoice_cash_rounding_id = fields.Many2one('account.cash.rounding',string='Cash Rounding Method')

    def _prepare_invoice(self):
        res = super()._prepare_invoice()
        temp1 = 0
        def compute_taxes(order_line):
            return order_line.taxes_id._origin.compute_all(**order_line._prepare_compute_all_values())

        for order in self:
            if order.invoice_cash_rounding_id.strategy == "biggest_tax":
                tax_lines_data = self.env['account.move']._prepare_tax_lines_data_for_totals_from_object(order.order_line, compute_taxes)
                for i in tax_lines_data:
                    if order.invoice_cash_rounding_id.rounding_method =="UP":
                        if 'tax_amount' in i:   
                            i['tax_amount'] += math.ceil(order.amount_total) - order.amount_total
                            temp1 = i['tax_amount']
                    elif order.invoice_cash_rounding_id.rounding_method =="DOWN":
                        if 'tax_amount' in i:
                            i['tax_amount'] += math.floor(order.amount_total) - order.amount_total
                            temp1 = i['tax_amount']
                    elif order.invoice_cash_rounding_id.rounding_method =="HALF-UP":
                        if 'tax_amount' in i:
                            temp = math.floor(i['tax_amount']) + 0.50
                            if i['tax_amount'] >= temp:
                                i['tax_amount'] += math.ceil(order.amount_total) - order.amount_total
                                temp1 = i['tax_amount']
                            elif i['tax_amount'] < temp:
                                i['tax_amount'] += math.floor(order.amount_total) - order.amount_total
                                temp1 = i['tax_amount']
        res.update({'amount_tax':temp1,
                    'invoice_cash_rounding_id':self.invoice_cash_rounding_id,
                    })
        return res
    
    @api.depends('order_line.taxes_id', 'order_line.price_subtotal', 'amount_total', 'amount_untaxed')
    def _compute_tax_totals_json(self):
        res = super()._compute_tax_totals_json()
        def compute_taxes(order_line):
            return order_line.taxes_id._origin.compute_all(**order_line._prepare_compute_all_values())

        for order in self:
            if order.product_id:
                temp1 = 0.00
                roundup = order.invoice_cash_rounding_id.rounding
                if order.invoice_cash_rounding_id.strategy == "biggest_tax":
                    tax_lines_data = self.env['account.move']._prepare_tax_lines_data_for_totals_from_object(order.order_line, compute_taxes)
                    for i in tax_lines_data:
                        if order.invoice_cash_rounding_id.rounding_method =="UP":
                            if 'tax_amount' in i:   
                                i['tax_amount'] += math.ceil(order.amount_total) - order.amount_total
                                temp1 = i['tax_amount']
                        elif order.invoice_cash_rounding_id.rounding_method =="DOWN":
                            if 'tax_amount' in i:
                                i['tax_amount'] += math.floor(order.amount_total) - order.amount_total
                                temp1 = i['tax_amount']
                        elif order.invoice_cash_rounding_id.rounding_method =="HALF-UP":
                            if 'tax_amount' in i:
                                temp = math.floor(i['tax_amount']) + 0.50
                                if i['tax_amount'] >= temp:
                                    i['tax_amount'] += math.ceil(order.amount_total) - order.amount_total
                                    temp1 = i['tax_amount']
                                elif i['tax_amount'] < temp:
                                    i['tax_amount'] += math.floor(order.amount_total) - order.amount_total
                                    temp1 = i['tax_amount']
                    tax_totals = self.env['account.move']._get_tax_totals(order.partner_id, tax_lines_data, order.amount_total, order.amount_untaxed, order.currency_id)
                    tax_totals['formatted_amount_total'] = tax_totals['amount_untaxed'] + temp1 + 0.00
                    order.tax_totals_json = json.dumps(tax_totals)
        return res

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





 # account_move = self.env['account.move']
        # for order in self:
            # tax_lines_data = account_move._prepare_tax_lines_data_for_totals_from_object(order.order_line, compute_taxes)
            # print("\n\n tax_lines_data",tax_lines_data)
            # tax_totals = account_move._get_tax_totals(order.partner_id, tax_lines_data, order.amount_total, order.amount_untaxed, order.currency_id)
            # print("\n\n tax_totals",tax_totals)
            # order.tax_totals_json = json.dumps(tax_totals)

    # @api.depends('order_line.price_total')
    # def _amount_all(self):
    #     super()._amount_all()
    #     for order in self:
    #         print("\n\n order in _amount_all")
    #         print("\n\n order.amount_tax1111",order.amount_tax)
    #         if order.invoice_cash_rounding_id.strategy == "biggest_tax":
    #             if order.invoice_cash_rounding_id.rounding_method =="UP":
    #                 if order.order_line.taxes_id:
    #                     print("\n\n order.amount_tax",order.amount_tax)
    #                     order.amount_tax = order.amount_tax + math.ceil(order.amount_total) - order.amount_total
    #                     print("\n\n order.amount_tax",order.amount_tax)
    #                 else :
    #                     order.amount_total = math.ceil(order.amount_total)
    #             elif order.invoice_cash_rounding_id.rounding_method =="DOWN":
    #                 order.amount_tax = math.floor(order.amount_tax)        