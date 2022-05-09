import json
import math
from odoo import api,models,fields
from odoo.exceptions import UserError

class PurchaseOrder(models.Model):
    _inherit = "purchase.order"

    round_of_cash = fields.Many2one('account.cash.rounding',string='Cash Rounding Method')
    line_ids = fields.One2many('purchase.order.line', 'move_id', string='Journal Items', copy=True, readonly=True,
        states={'draft': [('readonly', False)]})
    company_id = fields.Many2one(comodel_name='res.company', string='Company',
                                store=True, readonly=True,
                                compute='_compute_company_id')
    company_currency_id = fields.Many2one(string='Company Currency', readonly=True,
        related='company_id.currency_id')

    @api.onchange('round_of_cash','order_line')
    def _onchange_round_of_cash(self):
        def compute_taxes(order_line):
            return order_line.taxes_id._origin.compute_all(**order_line._prepare_compute_all_values())
        for order in self:
            temp1 = 0
            roundup = order.round_of_cash.rounding
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
                            if i['tax_amount'] > temp:
                                temp1 = i['tax_amount']=math.ceil(i['tax_amount'])
                            elif i['tax_amount'] < temp:
                                temp1 = i['tax_amount']=math.floor(i['tax_amount'])
                tax_totals = self.env['account.move']._get_tax_totals(order.partner_id, tax_lines_data, order.amount_total, order.amount_untaxed, order.currency_id)
                tax_totals['formatted_amount_total'] = tax_totals['amount_untaxed'] + temp1
                order.tax_totals_json = json.dumps(tax_totals)
            elif order.round_of_cash.strategy == "add_invoice_line":
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
                            if i['tax_amount'] > temp:
                                temp1 = i['tax_amount']=math.ceil(i['tax_amount'])
                            elif i['tax_amount'] < temp:
                                temp1 = i['tax_amount']=math.floor(i['tax_amount'])
                tax_totals = self.env['account.move']._get_tax_totals(order.partner_id, tax_lines_data, order.amount_total, order.amount_untaxed, order.currency_id)
                tax_totals['formatted_amount_total'] = tax_totals['amount_untaxed'] + temp1
                order.tax_totals_json = json.dumps(tax_totals)