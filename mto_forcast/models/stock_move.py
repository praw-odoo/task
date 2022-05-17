from odoo import api, models, fields

class StockMove(models.Model):
    _inherit = "stock.move"

    def _adjust_procure_method(self):
        for move in self:
            needed_qty = move.product_qty
            forecasted_qty = move.product_id.virtual_available
            if needed_qty > forecasted_qty:
                move.procure_method = 'make_to_order'
            elif needed_qty < forecasted_qty:
                super()._adjust_procure_method()