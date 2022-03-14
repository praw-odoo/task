
from odoo import api, models, fields
import sys

class SaleOrderLine(models.Model):
    _inherit = "stock.picking"

    # products = fields.Char(compute = "_compute_products")

    product_ids = fields.Many2many("product.product", compute = "_compute_products")

    @api.depends("move_ids_without_package.product_id")
    def _compute_products(self):
        for record in self:
            record.product_ids = record.move_ids_without_package.product_id.ids
            print("sys1", sys.getsizeof(record.move_ids_without_package.product_id.ids))
            print("sys2",sys.getsizeof(record.move_ids_without_package.product_id))
            print("\n\n\n ------------------------------------")

            
