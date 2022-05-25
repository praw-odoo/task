from odoo import api,models,fields

class MrpRoutingWorkcenter(models.Model):
    _inherit = "stock.warehouse.orderpoint"

    location_ids = fields.Many2many('stock.location', string='Locations')
    # get = fields.Many2one("stock.scheduler.compute")

    @api.depends('product_id', 'location_id', 'product_id.stock_move_ids', 'product_id.stock_move_ids.state', 'product_id.stock_move_ids.product_uom_qty','location_ids')
    def _compute_qty(self):
        super()._compute_qty()
        for order in self:
                for location in order.location_ids:
                    order.qty_on_hand = order.qty_on_hand + location.quant_ids.filtered(lambda pd: pd.product_id == order.product_id).available_quantity
                    