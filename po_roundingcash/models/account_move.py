import math, json
from odoo import api,models,fields

class AccountMove(models.Model):
    _inherit = "account.move"
    
    temp = 0.00
    @api.model
    def create(self, vals):
        global temp
        if 'amount_tax' in vals:
            temp = vals['amount_tax']
        self.invoice_cash_rounding_id = vals['invoice_cash_rounding_id']
        res = super().create(vals)
        return res

    @api.depends('line_ids.amount_currency', 'line_ids.tax_base_amount', 'line_ids.tax_line_id', 'partner_id', 'currency_id', 'amount_total', 'amount_untaxed')
    def _compute_tax_totals_json(self):
        super()._compute_tax_totals_json()
        # if self.invoice_cash_rounding_id.strategy == 'biggest_tax':    
        #     for move in self:
        #         if not move.is_invoice(include_receipts=True):
        #             move.tax_totals_json = None
        #             continue

        #         tax_lines_data = move._prepare_tax_lines_data_for_totals_from_invoice()
        #         for i in tax_lines_data:
        #             if 'tax_amount' in i:   
        #                 i['tax_amount'] = temp
        #         move.amount_total= move.amount_untaxed + temp
        #         move.tax_totals_json = json.dumps({
        #             **self._get_tax_totals(move.partner_id, tax_lines_data, move.amount_total, move.amount_untaxed, move.currency_id),
        #             'allow_tax_edition': move.is_purchase_document(include_receipts=False) and move.state == 'draft',
        #         })
        print("\n\n self.line_ids",self.line_ids)
        for line in self.line_ids:
            rounding_product_id = self.env.ref('po_roundingcash.product_product_round_off')
            if line.product_id == rounding_product_id:
                if self.invoice_cash_rounding_id.strategy == "add_invoice_line":
                    if self.invoice_cash_rounding_id.rounding_method =="UP":
                        line.account_id = self.invoice_cash_rounding_id.profit_account_id
                    elif self.invoice_cash_rounding_id.rounding_method =="DOWN":
                        line.account_id = self.invoice_cash_rounding_id.loss_account_id
                    else:
                        pass
            else:
                if self.invoice_cash_rounding_id.rounding_method =="UP":
                    line.account_id = self.invoice_cash_rounding_id.profit_account_id
                elif self.invoice_cash_rounding_id.rounding_method =="DOWN":
                    line.account_id = self.invoice_cash_rounding_id.loss_account_id





class AccountMoveLine(models.Model):
    _inherit = "account.move"

    @api.model_create_multi
    def create(self, vals):
        print("\n\n\n from line vals",vals)
        res = super().create(vals)
        return res

    













        # for move in self:
        #     if not move.is_invoice(include_receipts=True):
        #         Non-invoice moves don't support that field (because of multicurrency: all lines of the invoice share the same currency)
        #         move.tax_totals_json = None
        #         continue

        #     tax_lines_data = move._prepare_tax_lines_data_for_totals_from_invoice()
            
        #     move.tax_totals_json = json.dumps({
        #         **self._get_tax_totals(move.partner_id, tax_lines_data, move.amount_total, move.amount_untaxed, move.currency_id),
        #         'allow_tax_edition': move.is_purchase_document(include_receipts=False) and move.state == 'draft',
        #     })