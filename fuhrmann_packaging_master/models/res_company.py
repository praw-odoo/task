from odoo import api, fields, models


class Company(models.Model):
    _inherit = 'res.company'

    def _create_barcode_sequence(self):
        vals = []
        for company in self.env['res.company'].search([]):
            print('\n\n\n>>>>>>>>>', company)
            vals.append({
                'name': 'company',
                'code': 'gtin.stock.package.type',
                'company_id': company.id,
                'prefix': '00',
                'padding': 18,
                'number_next': 1,
                'number_increment': 1
            })
        if vals:
            self.env['ir.sequence'].create(vals)

    @api.model
    def create_missing_sequences(self):
        company_ids  = self.env['res.company'].search([])
        company_has_unbuild_seq = self.env['ir.sequence'].search([('code', '=', 'gtin.stock.package.type')]).mapped('company_id')
        company_todo_sequence = company_ids - company_has_unbuild_seq
        company_todo_sequence._create_barcode_sequence()

    def _create_per_company_sequences(self):
        self.ensure_one()
        self._create_barcode_sequence()
