from odoo import api, models, fields

class StockMove(models.Model):
    _inherit = "stock.move"

    # def _prepare_procurement_values(self):
    #     active_id = self._context.get("active_id")
    #     qty = self.env["sale.order"].browse(active_id).order_line
    #     values = super()._prepare_procurement_values()
    #     values['product_uom_qty'] = qty.product_uom_qty - qty.product_id.virtual_available
    #     return values


    def _adjust_procure_method(self):
        for move in self:
            needed_qty = move.product_qty
            forecasted_qty = move.product_id.virtual_available
            if needed_qty > forecasted_qty:
                # self._get_forecast_availability_outgoing(needed_qty-forecasted_qty)
                move.procure_method = 'make_to_order'
            elif needed_qty < forecasted_qty:
                super()._adjust_procure_method()