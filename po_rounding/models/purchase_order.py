import json
import math
from odoo import api,models,fields
from odoo.exceptions import UserError

class PurchaseOrder(models.Model):
    _inherit = "purchase.order"

    round_of_cash = fields.Many2one('account.cash.rounding',string='Cash Rounding Method')
    

    @api.onchange('round_of_cash','order_line')
    def _onchange_round_of_cash(self):
        print("\n\n\n _onchange_round_of_cash _onchange_round_of_cash")
        def compute_taxes(order_line):
            return order_line.taxes_id._origin.compute_all(**order_line._prepare_compute_all_values())
        for order in self:
            if order.product_id:
                temp1 = 0
                roundup = order.round_of_cash.rounding
                print("\n\n rounding",roundup)
                if order.round_of_cash.strategy == "biggest_tax":
                    tax_lines_data = self.env['account.move']._prepare_tax_lines_data_for_totals_from_object(order.order_line, compute_taxes)
                    for i in tax_lines_data:
                        if order.round_of_cash.rounding_method =="UP":
                            if 'tax_amount' in i:   
                                temp1 = i['tax_amount']=math.ceil(i['tax_amount'])
                        elif order.round_of_cash.rounding_method =="DOWN":
                            if 'tax_amount' in i:
                                temp1 = i['tax_amount']=math.floor(i['tax_amount'])
                        elif order.round_of_cash.rounding_method =="HALF-UP":
                            if 'tax_amount' in i:
                                temp = math.floor(i['tax_amount']) + 0.50
                                if i['tax_amount'] >= temp:
                                    temp1 = i['tax_amount']=math.ceil(i['tax_amount'])
                                elif i['tax_amount'] < temp:
                                    temp1 = i['tax_amount']=math.floor(i['tax_amount'])
                    tax_totals = self.env['account.move']._get_tax_totals(order.partner_id, tax_lines_data, order.amount_total, order.amount_untaxed, order.currency_id)
                    tax_totals['formatted_amount_total'] = tax_totals['amount_untaxed'] + temp1
                    order.tax_totals_json = json.dumps(tax_totals)
                    print('\'*100', json.dumps(tax_totals))
                elif order.round_of_cash.strategy == "add_invoice_line":
                    tax_lines_data = self.env['account.move']._prepare_tax_lines_data_for_totals_from_object(order.order_line, compute_taxes)
                    for i in tax_lines_data:        
                        if order.round_of_cash.rounding_method =="UP":
                            import datetime
                            if 'tax_amount' in i:
                                temp1 = math.ceil(i['tax_amount']) - i['tax_amount']
                                vals = {
                            'product_id': False,
                                'order_id': order._origin.id,
                            'name': self.round_of_cash.name,
                                'company_id': order.company_id.id,
                            'product_qty': 1,
                            'product_uom': 1,
                            'price_unit': temp1,
                            'display_type': False,
                            'date_planned': datetime.datetime.now(),
                                }
                                self.order_line = [(0,0,vals)]
                        elif order.round_of_cash.rounding_method =="DOWN":
                            print("\n\n calling down")
                            if 'tax_amount' in i:
                                temp1 = math.floor(i['tax_amount']) - i['tax_amount']
                                print("\n\n i",i)
                                vals = {
                                'order_id': order._origin.id,
                                'name': self.round_of_cash.name,
                                'company_id': order.company_id.id,
                                'product_qty': 1,
                                'price_unit': temp1,
                                }
                                for line in self:
                                    print("\n\n line",line._origin)
                                    if not line.product_id:
                                        line.unlink()
                                print("\n\n self.order_line",len(self.order_line))
                                self.order_line = [(0,0,vals)]
                        elif order.round_of_cash.rounding_method =="HALF-UP":
                            if 'tax_amount' in i:
                                temp = math.floor(i['tax_amount']) + 0.50
                                if i['tax_amount'] >= temp:
                                    temp1 = math.ceil(i['tax_amount']) - i['tax_amount']
                                    vals = {
                                    'order_id': order._origin.id,
                                    'name': self.round_of_cash.name,
                                    'company_id': order.company_id.id,
                                    'product_qty': 1,
                                    'price_unit': temp1,
                                    }
                                    print("\n\n self.order_line",len(self.order_line))
                                    self.order_line = [(0,0,vals)]
                                elif i['tax_amount'] < temp:
                                    temp1 = math.floor(i['tax_amount']) - i['tax_amount']
                                    print("\n\n i",i)
                                    vals = {
                                    'order_id': order._origin.id,
                                    'name': self.round_of_cash.name,
                                    'company_id': order.company_id.id,
                                    'product_qty': 1,
                                    'price_unit': -temp1,
                                    }
                                    print("\n\n self.order_line",len(self.order_line))
                                    print("\n\n calling vals")
                    tax_totals = self.env['account.move']._get_tax_totals(order.partner_id, tax_lines_data, order.amount_total, order.amount_untaxed, order.currency_id)
                    # tax_totals['formatted_amount_total'] = tax_totals['amount_untaxed'] + temp1
                    order.tax_totals_json = json.dumps(tax_totals)




















# self.line_ids = [(0,0,vals1)]
                            # print("\n\n order.vals1",order._origin.order_line.price_unit)
                            # # order._origin.line_ids.create((0,0,vals1))

# aa=self.env["purchase.order.line"].create(vals)
                            # order._origin.order_line.ids.append((0, 0,  {
                            # 'order_id': order._origin.id,
                            # 'name': self.round_of_cash.name,
                            # 'account_id': self.round_of_cash.profit_account_id.id,
                            # 'company_id': order._origin.company_id.id,
                            # 'company_currency_id': order._origin.company_currency_id.id,
                            # 'product_qty': 1,
                            # 'price_unit': temp1,
                            # }))
                            # print("OOOOOOOOOOOOOO", order._origin.order_line)