
from odoo import api, models, fields

class SaleOrderLine(models.Model):
    _inherit = "stock.picking"

    # products = fields.Char(compute = "_compute_products")

    product_ids = fields.Many2many("product.product", compute = "_compute_products")
    @api.depends("move_ids_without_package.product_id")
    def _compute_products(self):
        for record in self:
            record.product_ids = record.move_ids_without_package.product_id.ids
            print(type(record.move_ids_without_package.product_id.ids))
            print(type(record.move_ids_without_package.product_id))

            

    # @api.onchange("product_id")
    # def _onchange_products(self):
    #      for record in self:
    #          for line in record:
    #             record.products += line.product_id