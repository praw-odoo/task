# -*- coding: utf-8 -*-
# Part of Odoo. See LICENSE file for full copyright and licensing details.

from odoo import fields, models


class StockPackageType(models.Model):
    _inherit = 'stock.package.type'

    auto_create_gtin = fields.Boolean(string="Auto-Create GTIN")
