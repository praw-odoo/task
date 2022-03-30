from odoo import api, models,fields


class SaleOrder(models.Model):
    _inherit = "sale.order"

    def add_in_cart(self):
        print("\n\n hello")
        products = self.order_line.filtered(lambda x: x.product_id)
        length = len(products)
        print("\n\n length",length)