from odoo import api, fields, models


class ProductSupplierinfo(models.Model):
    _inherit = 'product.supplierinfo'

    minimum_qty = fields.Float(String="Min. Quantity")
    