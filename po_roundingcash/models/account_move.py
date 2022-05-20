import math, json
from tempfile import tempdir
from odoo import api,models,fields

class AccountMove(models.Model):
    _inherit = "account.move"

    
    temp = 0.00
    @api.model
    def create(self, vals):
        global temp
        temp = vals['amount_tax']
        print("\n\n temp",temp)
        res = super().create(vals)
        print("\n\n temp",temp)
        return res

    @api.depends('line_ids.amount_currency', 'line_ids.tax_base_amount', 'line_ids.tax_line_id', 'partner_id', 'currency_id', 'amount_total', 'amount_untaxed')
    def _compute_tax_totals_json(self):
        
        super()._compute_tax_totals_json()
        for move in self:
            if not move.is_invoice(include_receipts=True):
                # Non-invoice moves don't support that field (because of multicurrency: all lines of the invoice share the same currency)
                move.tax_totals_json = None
                continue

            tax_lines_data = move._prepare_tax_lines_data_for_totals_from_invoice()
            for i in tax_lines_data:
                print("\n\n i",i)
                if 'tax_amount' in i:   
                    i['tax_amount'] = temp
                    print("\n\n i['tax_amount']",i['tax_amount'])
            print("\n\n tax_lines_data from base",tax_lines_data)
            move.amount_total= move.amount_untaxed + temp
            move.tax_totals_json = json.dumps({
                **self._get_tax_totals(move.partner_id, tax_lines_data, move.amount_total, move.amount_untaxed, move.currency_id),
                'allow_tax_edition': move.is_purchase_document(include_receipts=False) and move.state == 'draft',
            })















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