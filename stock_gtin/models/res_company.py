# -*- coding: utf-8 -*-
# Part of Odoo. See LICENSE file for full copyright and licensing details.

from odoo import api, fields, models


class Company(models.Model):
    _inherit = 'res.company'

    def _create_sequence_for_new_company(self):
        unbuild_vals = []
        for company in self:
            unbuild_vals.append({
                'name': 'Unbuild',
                'code': 'pack.order',
                'company_id': company.id,
                'prefix': 'GTIN/',
                'padding': 18,
                'number_next': 1,
                'number_increment': 1
            })
        if unbuild_vals:
            self.env['ir.sequence'].create(unbuild_vals)

    @api.model
    def create_missing_sequences(self):
        company_ids  = self.env['res.company'].search([])
        company_has_unbuild_seq = self.env['ir.sequence'].search([('code', '=', 'pack.order')]).mapped('company_id')
        company_todo_sequence = company_ids - company_has_unbuild_seq
        company_todo_sequence._create_sequence_for_new_company()

    def _create_per_company_sequences(self):
        super(Company, self)._create_per_company_sequences()
        self._create_sequence_for_new_company()
