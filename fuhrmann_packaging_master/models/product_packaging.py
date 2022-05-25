# -*- coding: utf-8 -*-
# Part of Odoo. See LICENSE file for full copyright and licensing details.

from odoo import api, fields, models


class ProductPackaging(models.Model):
    _inherit = 'product.packaging'

    length = fields.Float(string="Length")
    width = fields.Float(string="Width")
    height = fields.Float(string="Height")
    weight = fields.Float(string="Weight")

    @api.model
    def create(self, values):
        res = super().create(values)
        if not res.barcode and res.package_type_id.auto_create_gtin:
            res.barcode = self.env['ir.sequence'].next_by_code('gtin.stock.package.type')
        return res

    def write(self, vals):
        res = super().write(vals)
        if vals.get('package_type_id'):
            package_type_id = self.env['stock.package.type'].browse(vals.get('package_type_id'))
            if not self.barcode and package_type_id.auto_create_gtin:
                self.barcode = self.env['ir.sequence'].next_by_code('gtin.stock.package.type')
        return res
